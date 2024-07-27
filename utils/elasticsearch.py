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
    except RequestError as e:
        if e.info.get('error', {}).get('type') == 'resource_already_exists_exception':
            print(f"Found an existing index with name {index_name}, nothing to do.")
        else:
            print(e)
        
    

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
    idx = 0

    for doc in tqdm(documents):
        try:
            es_client.index(index=index_name, document=doc, timeout=f"{timeout}s")
        except RequestError as e:
            print(f"{e}", "index:", idx, "-> Skipped...")
            n_skipped += 1
            pass
    
        idx += 1

    n_parsed = n_documents - n_skipped  
    print(
        f"Successfully indexed {n_parsed}/{n_documents} documents in index {index_name}"
    )


def get_index_mapping(es_client, index_name):
    try:
        # Retrieve the mapping for the given index
        mapping = es_client.indices.get_mapping(index=index_name)
        
        # Extract the properties section which contains the field mappings
        properties = mapping[index_name]['mappings']['properties']
        
        # Extract field names and their types
        field_types = {field: properties[field]['type'] for field in properties}
        
        return field_types
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


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


def knn_elastic_search(
    **kwargs,
):
    es_client = kwargs.get('es_client')
    index_name = kwargs.get('index_name')
    query_vector = kwargs.get('query_vector')
    filter_dict = kwargs.get('filter_dict', {})
    field = kwargs.get('field', "text_vector")
    k = kwargs.get('k', 5)
    num_candidates = kwargs.get('num_candidates', 10_000)
    num_results = kwargs.get('num_results', 5)

    knn_query = {
        "field": field,
        "query_vector": query_vector,
        "k": k,
        "num_candidates": num_candidates
    }

    responses = es_client.search(
        index=index_name,
        query={
            "match": filter_dict,
        },
        knn=knn_query,
        size=num_results,
    )["hits"]["hits"]
    
    
    for i in range(len(responses)):
        responses[i]["_source"] =\
            {
                key: value for key, value in\
                    responses[i]["_source"].items()\
                    if not key.endswith('_vector')
            }
        responses[i]['id'] = responses[i]["_source"]['id']

    return responses