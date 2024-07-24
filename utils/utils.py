import json
import os
from dotenv import load_dotenv


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