import json
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import (
    ConnectionError,
    NotFoundError,
    RequestError
)
from exceptions.exceptions import (
    ElasticsearchConnectionError,
)
from tqdm.auto import tqdm

def create_elasticsearch_client(
        host,
        port
):
    try:
        es_client = Elasticsearch(f'http://{host}:{port}')
        # Perform a simple request to check if the connection is successful
        if not es_client.ping():
            raise ElasticsearchConnectionError("Could not connect to Elasticsearch")
        print("Connected to Elasticsearch")
        return es_client
    except ConnectionError as e:
        raise ElasticsearchConnectionError("ConnectionError: Could not connect to Elasticsearch") from e


def create_elasticsearch_index(
        es_client,
        index_name,
        index_settings,
        timeout=60
):
    try:
        es_client.indices.create(index=index_name, body=index_settings, timeout=f"{timeout}s")
        print(f"Successfully created index {index_name}.")
    except RequestError:
        print(f"Found an existing index with name {index_name}, nothing to do.")
    

def search_elasticsearch_indecis(
        es_client,
):
    indices = [
        index for index in es_client.indices.get_alias(index="*")
    ]
    return indices


def remove_elasticsearch_index(
        es_client,
        index_name,
):
    try:
        es_client.indices.delete(index=index_name)
        print(f"Successfully removed index {index_name}.")

    except NotFoundError:
        print(f"Found no index with name {index_name}, nothing to remove.")


def load_index_settings(index_settings_path):
    with open(index_settings_path, 'rt') as f_in:
        index_settings = json.load(f_in)
    return index_settings


def index_documents(
    es_client, index_name, documents, timeout=60
):
    n_skipped = 0
    n_documents = documents.__len__()
    for i, doc in tqdm(enumerate(documents)):
        try:
            es_client.index(index=index_name, document=doc, timeout=f"{timeout}s")
        except RequestError as e:
            print(f"{e}", "index:", i, "-> Skipped...")
            n_skipped += 1
            pass

    n_parsed = n_documents - n_skipped  
    print(
        f"Successfully indexed {n_parsed}/{n_documents} documents in index {index_name}"
    )


def elastic_search(es_client, index_name, query, filter_dict, boost, num_results):
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
                            f"section^{boost.get('section', 1)}"
                        ],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": filter_dict
                }
            }
        }
    }

    response = es_client.search(index=index_name, body=search_query)
    
    result_docs = []
    
    for hit in response['hits']['hits']:
        result_docs.append(hit['_source'])
    
    return result_docs