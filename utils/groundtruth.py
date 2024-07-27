import pandas as pd
from tqdm.auto import tqdm
from utils.query import(
    build_prompt,
    llm,
)
from utils.utils import (
    parse_json_response
)

def generate_questions_using_openai(
    client, prompt_template_path, documents, model_name='gpt-4o'
):   
    generated_questions_dict = {}

    for doc in tqdm(documents):
        doc_id = doc["id"]
        
        if doc_id in generated_questions_dict:
            continue
        
        prompt = build_prompt(
            prompt_template_path=prompt_template_path, 
            document_dict=doc
        )
        
        json_response = llm(client, prompt, model_name)
        
        generated_questions = parse_json_response(json_response)
        generated_questions_dict[doc_id] = generated_questions

    doc_index = {d['id']: d for d in documents}

    final_results = []
    for doc_id, questions in generated_questions_dict.items():
        course = doc_index[doc_id]['course']
        for q in questions:
            final_results.append((q, course, doc_id))

    return pd.DataFrame(
        final_results, columns=['question', 'course', 'document']
    )