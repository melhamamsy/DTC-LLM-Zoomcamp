import os
from tqdm.auto import tqdm


def setup_hf_cache_dir(path):
    os.environ['HF_HOME'] = path
    print(f"""HuggingFace cache directory
($HF_HOME) has been set to: {path}
"""
    )

def setup_transformers_cache_dir(path):
    os.environ['TRANSFORMERS_CACHE'] = path
    print(
        f"""HuggingFace transformers cache directory 
($TRANSFORMERS_CACHE) has been set to: {path}
"""
    )

def setup_sentence_transformers_cache_dir(path):
    os.environ['SENTENCE_TRANSFORMERS_HOME'] = path
    print(
        f"""HuggingFace sentenct transformers cache directory
($SENTENCE_TRANSFORMERS_HOME) has been set to: {path}
"""
    )

def vectorize_sentences(
        model, documents, field="text"
):
    vectorized_documents = []
    for doc in tqdm(documents):
        # Transforming the title into an embedding using the model
        doc[f"{field}_vector"] = model.encode(doc[field]).tolist()
        vectorized_documents.append(doc)
    
    return vectorized_documents   