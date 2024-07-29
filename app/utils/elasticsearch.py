"""
This module provides utility functions for interacting with Elasticsearch.
It includes functions to create an Elasticsearch client, manage indices, 
search, and index documents.
Custom exceptions are also handled for connection and query errors.
"""

import json

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import (NotFoundError,
                                      RequestError)
from tqdm.auto import tqdm

from exceptions.exceptions import ElasticsearchConnectionError


def create_elasticsearch_client(host, port):
    """
    Create and return an Elasticsearch client.

    Args:
        host (str): The hostname for the Elasticsearch instance.
        port (int): The port for the Elasticsearch instance.

    Returns:
        Elasticsearch: An Elasticsearch client instance.

    Raises:
        ElasticsearchConnectionError: If the connection to Elasticsearch fails.
    """
    try:
        es_client = Elasticsearch(f"http://{host}:{port}")
        # Perform a simple request to check if the connection is successful
        if not es_client.ping():
            raise ElasticsearchConnectionError("Could not connect to Elasticsearch")
        print("Connected to Elasticsearch")
        return es_client
    except ConnectionError as e:
        raise ElasticsearchConnectionError(
            "ConnectionError: Could not connect to Elasticsearch"
        ) from e


def create_elasticsearch_index(es_client, index_name, index_settings, timeout=60):
    """
    Create an Elasticsearch index with the specified settings.

    Args:
        es_client (Elasticsearch): The Elasticsearch client instance.
        index_name (str): The name of the index to create.
        index_settings (dict): The settings for the index.
        timeout (int): The timeout for the index creation request in seconds. Default is 60.
    """
    try:
        es_client.indices.create(
            index=index_name, body=index_settings, timeout=f"{timeout}s"
        )
        print(f"Successfully created index {index_name}.")
    except RequestError as e:
        if e.info.get("error", {}).get("type") == "resource_already_exists_exception":
            print(f"Found an existing index with name {index_name}, nothing to do.")
        else:
            print(e)


def search_elasticsearch_indecis(
    es_client,
):
    """
    Retrieve and return the list of indices in the Elasticsearch cluster.

    Args:
        es_client (Elasticsearch): The Elasticsearch client instance.

    Returns:
        list: A list of index names.
    """
    indices = list(es_client.indices.get_alias(index='*'))
    return indices


def get_indexed_documents_count(
        es_client, 
        index_name,
):
    """
    """
    return es_client.count(index=index_name)


def remove_elasticsearch_index(
    es_client,
    index_name,
):
    """
    Remove an Elasticsearch index.

    Args:
        es_client (Elasticsearch): The Elasticsearch client instance.
        index_name (str): The name of the index to remove.
    """
    try:
        es_client.indices.delete(index=index_name)
        print(f"Successfully removed index {index_name}.")

    except NotFoundError:
        print(f"Found no index with name {index_name}, nothing to remove.")


def load_index_settings(index_settings_path):
    """
    Load and return the index settings from a JSON file.

    Args:_
        index_settings_path (str): The file path to the index settings JSON file.

    Returns:
        dict: The index settings.
    """
    with open(index_settings_path, "rt", encoding="utf-8") as f_in:
        index_settings = json.load(f_in)
    return index_settings


def index_document(es_client, index_name, document, timeout=60):
    """
    Index multiple documents into an Elasticsearch index.

    Args:
        es_client (Elasticsearch): The Elasticsearch client instance.
        index_name (str): The name of the index.
        documents (list): A list of documents to index.
        timeout (int): The timeout for indexing requests in seconds. Default is 60.
    """
    try:
        es_client.index(index=index_name, document=document, timeout=f"{timeout}s")
    except RequestError as e:
        print(f"{e}", "id:", document['id'], "-> Skipped...")


def get_index_mapping(es_client, index_name):
    """
    Retrieve and return the mapping for an Elasticsearch index.

    Args:
        es_client (Elasticsearch): The Elasticsearch client instance.
        index_name (str): The name of the index.

    Returns:
        dict: A dictionary containing field names and their types, or None if an error occurs.
    """
    try:
        # Retrieve the mapping for the given index
        mapping = es_client.indices.get_mapping(index=index_name)

        # Extract the properties section which contains the field mappings
        properties = mapping[index_name]["mappings"]["properties"]

        # Extract field names and their types
        field_types = {field: properties[field]["type"] for field in properties}

        return field_types

    except RequestError as e:
        print(f"An error occurred: {e}")
        return None


def elastic_search(es_client, index_name, query, **kwargs):
    """
    Perform a search query on an Elasticsearch index.

    Args:
        es_client (Elasticsearch): The Elasticsearch client instance.
        index_name (str): The name of the index to search.
        query (str): The search query.
        **kwargs: Arbitrary keyword arguments including:
            filter_dict (dict): A dictionary of filter terms. 
                Defaults to an empty dictionary.
            boost (dict): A dictionary of boost values for specific fields. 
                Defaults to an empty dictionary.
            num_results (int): The number of search results to return. 
                Defaults to 5.

    Returns:
        list: A list of documents matching the search query.
    """
    filter_dict = kwargs.get('filter_dict', {})
    boost = kwargs.get('boost', {})
    num_results = kwargs.get('num_results', 5)

    search_query = {
        "size": num_results,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            f"question^{boost.get('question', 1)}",
                            f"text^{boost.get('text', 1)}",
                            f"section^{boost.get('section', 1)}",
                        ],
                        "type": "best_fields",
                    }
                },
                "filter": {"term": filter_dict},
            }
        },
    }

    response = es_client.search(index=index_name, body=search_query)

    result_docs = []

    for hit in response["hits"]["hits"]:
        result_docs.append(hit["_source"])

    return result_docs


def knn_elastic_search(
    **kwargs,
):
    """
    Perform a k-nearest neighbors (kNN) search query on an Elasticsearch index.

    Args:
        **kwargs: Arbitrary keyword arguments including es_client, index_name, 
            query_vector, filter_dict, field, k, num_candidates, and num_results.

    Returns:
        list: A list of documents matching the kNN search query.
    """
    es_client = kwargs.get("es_client")
    index_name = kwargs.get("index_name")
    query_vector = kwargs.get("query_vector")
    filter_dict = kwargs.get("filter_dict", {})
    field = kwargs.get("field", "text_vector")
    k = kwargs.get("k", 5)
    num_candidates = kwargs.get("num_candidates", 10_000)
    num_results = kwargs.get("num_results", 5)

    knn_query = {
        "field": field,
        "query_vector": query_vector,
        "k": k,
        "num_candidates": num_candidates,
    }

    responses = es_client.search(
        index=index_name,
        query={
            "match": filter_dict,
        },
        knn=knn_query,
        size=num_results,
    )["hits"]["hits"]

    for response in responses:
        response["_source"] = {
            key: value
            for key, value in response["_source"].items()
            if not key.endswith("_vector")
        }
        response["id"] = response["_source"]["id"]

    return responses
