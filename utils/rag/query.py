from utils.rag.elasticsearch import elastic_search
from exceptions.exceptions import SearchContextWrongValueError


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


def llm(client, prompt, model='gpt-4o'):
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content


def rag(**kwargs):

    es_client = kwargs.get('es_client')
    query = kwargs.get('query')
    index = kwargs.get('index')
    index_name = kwargs.get('index_name')
    filter_dict = kwargs.get('filter_dict')
    boost = kwargs.get('boost')
    num_results = kwargs.get('num_results')
    prompt_template_path = kwargs.get('prompt_template_path')
    client = kwargs.get('client')
    model = kwargs.get('model')
    search_context = kwargs.get('search_context', 'minsearch')

    if search_context == 'minsearch':
        search_results = search(query, index, filter_dict, boost, num_results)
    elif search_context == 'elasticsearch':
        search_results = elastic_search(es_client, index_name, query, filter_dict, boost, num_results)
    else:
        raise SearchContextWrongValueError(
            "Parameter `search_context` value must be in ['minsearch', 'elasticsearch'] or None"
        )

    prompt = build_prompt(query, search_results, prompt_template_path)
    answer = llm(client, prompt, model)
    return answer