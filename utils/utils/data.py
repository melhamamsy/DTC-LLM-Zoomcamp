import json


def load_json_document(path):
    with open(path, 'rt') as f_in:
        docs_raw = json.load(f_in)
    documents = []

    for course_dict in docs_raw:
        for doc in course_dict['documents']:
            doc['course'] = course_dict['course']
            documents.append(doc)

    return documents