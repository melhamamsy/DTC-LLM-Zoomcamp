import json
import os
from dotenv import load_dotenv
import hashlib
import re


def find_parameters(text):
    pattern = r'\{(.*?)\}'
    return re.findall(pattern, text)


def is_sublist(main_list, sublist):
    n = len(sublist)
    return any(sublist == main_list[i:i+n] for i in range(len(main_list) - n + 1))


def initialize_env_variables(project_root = None):
    # Construct the full path to the .env file
    if not project_root:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))

    dotenv_path = os.path.join(project_root, '.env')

    print("Initialized environment variables listed in:",dotenv_path)
    # Load the .env file
    load_dotenv(dotenv_path)


def load_json_document(path):
    with open(path, 'rt') as f_in:
        docs_raw = json.load(f_in)
    documents = []

    for course_dict in docs_raw:
        for doc in course_dict['documents']:
            doc['course'] = course_dict['course']
            documents.append(doc)

    return documents


def find_duplicates(lst):
    index_dict = {}
    
    for index, item in enumerate(lst):
        if item in index_dict:
            index_dict[item].append(index)
        else:
            index_dict[item] = [index]
    
    duplicates = [tuple(indices) for indices in index_dict.values() if len(indices) > 1]
    
    return duplicates


def generate_document_id(doc):
    # combined = f"{doc['course']}-{doc['question']}"
    combined = f"{doc['course']}-{doc['question']}-{doc['text'][:10]}"
    hash_object = hashlib.md5(combined.encode())
    hash_hex = hash_object.hexdigest()
    document_id = hash_hex[:8]
    return document_id


def id_documents(docs):
    ## We might need to return hashes dict
    for doc in docs:
        doc['id'] = generate_document_id(doc)

    return docs


def correct_json_string(input_string):
    # Replace single backslashes with double backslashes
    corrected_string = input_string.replace('\\', '\\\\')
    return corrected_string


def parse_json_response(response):
    try:
        return json.loads(
            response
        )
    except ValueError as e:
        return json.loads(
            correct_json_string(
                response
            )
        )