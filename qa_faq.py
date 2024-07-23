import streamlit as st

import sys
import os

PROJECT_DIR = "/mnt/workspace/__ing/llming/DTC/course"
sys.path.append(PROJECT_DIR)

from utils.rag.elasticsearch import (
    create_elasticsearch_client,
    load_index_settings,
)

from utils.rag.query import rag
from openai import OpenAI


## =======> ollama setup:
ollama_host = "localhost"
ollama_port = "11434"

client = OpenAI(
    base_url=f'http://{ollama_host}:{ollama_port}/v1/',
    api_key='ollama',
)


## =======> elastic search setup:
es_host = "localhost"
es_port = 9200
index_name = "course-questions"
index_settings_path = os.path.join(
    PROJECT_DIR,
    "config/elasticsearch/course_qa_index_settings.json"
)
index_settings = load_index_settings(index_settings_path)

es_client = create_elasticsearch_client(es_host, es_port)


## =======> rag setup:
model_name = "phi3"
search_context = 'elasticsearch'
boost = {'question': 3.0, 'section': 0.5}
filter_dict={'course': 'data-engineering-zoomcamp'}
num_results = 5
prompt_template_path = os.path.join(PROJECT_DIR,"prompts/course_qa.txt")

rag_params = dict(
    es_client=es_client,
    client=client,
    query=None,
    index_name=index_name,
    filter_dict=filter_dict,
    boost=boost,
    num_results=num_results,
    prompt_template_path=prompt_template_path,
    model=model_name,
    search_context=search_context
)


def main():
    st.title("RAG Function Invocation")

    user_input = st.text_input("Enter your input:")

    if st.button("Ask"):
        with st.spinner('Processing...'):
            rag_params['query'] = user_input
            output = rag(**rag_params)
            st.success("Completed!")
            st.write(output)
            rag_params['query'] = None

if __name__ == "__main__":
    main()