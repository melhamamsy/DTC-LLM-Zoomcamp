"""
This module sets up a Streamlit application for invoking a 
Retrieval-Augmented Generation (RAG) function.
It configures necessary clients and parameters for interacting 
with OpenAI's API and Elasticsearch.
The application allows users to input queries,
which are processed using the RAG method.

Setup:
- OpenAI client (Ollama backend) for handling API requests.
- Elasticsearch client for querying a specified index.
- Parameters for the RAG function, including model name, 
search context, boosting factors, and filter criteria.

The main function renders a simple Streamlit interface with a text 
input for user queries and a button to trigger the RAG function.
The results are displayed within the Streamlit app.
"""

import os

import streamlit as st
from openai import OpenAI

from utils.elasticsearch import create_elasticsearch_client
from utils.query import rag

## =======> project path:
PROJECT_DIR = "/mnt/workspace/__ing/llming/DTC/course"

## =======> ollama setup:
OLLAMA_HOST = "localhost"
OLLAMA_PORT = "11434"

CLIENT = OpenAI(
    base_url=f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/v1/",
    api_key="ollama",
)


## =======> elastic search setup:
ES_HOST = "localhost"
ES_PORT = 9200
INDEX_NAME = "course-questions"
ES_CLIENT = create_elasticsearch_client(ES_HOST, ES_PORT)


## =======> rag setup:
MODEL_NAME = "phi3"
SEARCH_CONTEXT = "elasticsearch"
BOOST = {"question": 3.0, "section": 0.5}
FILTER_DICT = {"course": "data-engineering-zoomcamp"}
NUM_RESULTS = 5
PROMPT_TEMPLATE_PATH = os.path.join(PROJECT_DIR, "prompts/course_qa.txt")

RAG_PARAMS = {
    'es_client':ES_CLIENT,
    'client':CLIENT,
    'query':None,
    'index_name':INDEX_NAME,
    'filter_dict':FILTER_DICT,
    'boost':BOOST,
    'num_results':NUM_RESULTS,
    'prompt_template_path':PROMPT_TEMPLATE_PATH,
    'model_name':MODEL_NAME,
    'search_context':SEARCH_CONTEXT,
}


def main():
    """
    Main function to render the Streamlit interface for invoking 
    the RAG function.
    
    The interface includes:
    - A text input box for the user to enter a query.
    - A button to submit the query.
    
    When the button is clicked, the RAG function is called with 
    the user's query and configured parameters. The result is 
    displayed within the Streamlit app.
    """
    st.title("RAG Function Invocation")

    user_input = st.text_input("Enter your input:")

    if st.button("Ask"):
        with st.spinner("Processing..."):
            RAG_PARAMS["query"] = user_input
            output = rag(**RAG_PARAMS)
            st.success("Completed!")
            st.write(output)
            RAG_PARAMS["query"] = None


if __name__ == "__main__":
    main()
