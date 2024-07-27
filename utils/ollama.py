from tqdm.auto import tqdm

def get_embedding(client, text, model_name='locusai/multi-qa-minilm-l6-cos-v1'):
    text = text.replace("\n", " ")
    return client.embeddings.create(
        input = [text], model=model_name
    ).data[0].embedding


def embed_documents(client, documents, model_name):
    for doc in tqdm(documents):
        question = doc['question']
        text = doc['text']
        qt = question + ' ' + text

        doc["text_vector"] =\
            get_embedding(
                client=client, 
                text=text, 
                model_name=model_name
            )
        doc["question_vector"] =\
            get_embedding(
                client=client, 
                text=question, 
                model_name=model_name
            )
        doc["question_text_vector"] =\
            get_embedding(
                client=client, 
                text=qt, 
                model_name=model_name
            )
        
    return documents