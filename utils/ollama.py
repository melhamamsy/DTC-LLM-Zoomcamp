"""
This module provides utility functions for ollama.
The utility functions are used to:
    1. Embed a document using specified model (must be available in ollama)
    2. Embed a batch of documents with 'questions' and 'text' keys.
    3. ...
"""

from tqdm.auto import tqdm


def get_embedding(client, text, model_name="locusai/multi-qa-minilm-l6-cos-v1"):
    """
    Get the embedding for a given text using a specified model.

    Args:
        client: The client instance to use for generating embeddings.
        text (str): The text to be embedded.
        model_name (str, optional): The name of the model to use
        for embedding. Default is 'locusai/multi-qa-minilm-l6-cos-v1'.

    Returns:
        list: The embedding of the text as a list of floats.
    """
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model_name).data[0].embedding


def embed_documents(client, documents, model_name):
    """
    Embed multiple documents using a specified model.

    Args:
        client: The client instance to use for generating embeddings.
        documents (list): A list of documents where each document is
        a dictionary containing 'question' and 'text' fields.
        model_name (str): The name of the model to use for embedding.

    Returns:
        list: A list of documents with added embeddings for 'text',
        'question', and combined 'question_text' fields.
    """
    for doc in tqdm(documents):
        question = doc["question"]
        text = doc["text"]
        qt = question + " " + text

        doc["text_vector"] = get_embedding(
            client=client, text=text, model_name=model_name
        )
        doc["question_vector"] = get_embedding(
            client=client, text=question, model_name=model_name
        )
        doc["question_text_vector"] = get_embedding(
            client=client, text=qt, model_name=model_name
        )

    return documents
