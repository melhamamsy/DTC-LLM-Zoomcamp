from utils.elasticsearch import elastic_search
from exceptions.exceptions import SearchContextWrongValueError

from transformers import T5Tokenizer, T5ForConditionalGeneration



def search(query, index, filter_dict=None, boost=None, num_results=5):
    if not boost:
        boost = {}
        
    if not filter_dict:
        filter_dict = {}
    
    results = index.search(
        query=query,
        filter_dict=filter_dict,
        boost_dict=boost,
        num_results=num_results
    )

    return results


def build_prompt(query, search_results, prompt_template_path):
    with open(prompt_template_path, 'r') as f:
        prompt_template = f.read().strip()

    context = ""
    
    for doc in search_results:
        context = context + f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}\n\n"
    
    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt


def llm(client, prompt, model_name='gpt-4o', generate_params={}):  
    if model_name in ['gpt-4o', 'phi3']:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content

    elif model_name == 'google/flan-t5-small':
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        llm_model = T5ForConditionalGeneration.from_pretrained(model_name, device_map="auto")

        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")
        outputs = llm_model.generate(
            input_ids,
            max_length=generate_params.get("max_length", 100),
            num_beams=generate_params.get("num_beams", 5),
            do_sample=generate_params.get("do_sample", False),
            temperature=generate_params.get("temperature", 1.0),
            top_k=generate_params.get("top_k", 50),
            top_p=generate_params.get("top_p", 0.95),
        )
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return result


def rag(**kwargs):

    es_client = kwargs.get('es_client')
    client = kwargs.get('client')
    query = kwargs.get('query')
    index = kwargs.get('index')
    index_name = kwargs.get('index_name')
    filter_dict = kwargs.get('filter_dict')
    boost = kwargs.get('boost')
    num_results = kwargs.get('num_results')
    prompt_template_path = kwargs.get('prompt_template_path')
    model_name = kwargs.get('model_name')
    search_context = kwargs.get('search_context', 'minsearch')
    generate_params = kwargs.get('generate_params', {})

    if search_context == 'minsearch':
        search_results = search(query, index, filter_dict, boost, num_results)
    elif search_context == 'elasticsearch':
        search_results = elastic_search(es_client, index_name, query, filter_dict, boost, num_results)
    else:
        raise SearchContextWrongValueError(
            "Parameter `search_context` value must be in ['minsearch', 'elasticsearch'] or None"
        )

    prompt = build_prompt(query, search_results, prompt_template_path)
    answer = llm(client, prompt, model_name, generate_params)
    return answer