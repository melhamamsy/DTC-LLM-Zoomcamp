"""
This module provides functions for searching and generating
prompts using various models. It includes functions to search
using MinSearch or Elasticsearch, build context from search
results, construct prompts from templates, and generate
responses using language models.
"""

from transformers import T5ForConditionalGeneration, T5Tokenizer

from exceptions.exceptions import (
    SearchContextWrongValueError,
    WrongPomptParams,
    ModelNotCached,
)
from utils.elasticsearch import elastic_search
from utils.utils import find_parameters, is_sublist


def search(query, index, filter_dict=None, boost=None, num_results=5):
    """
    Perform a search using MinSearch.

    Args:
        query (str): The search query.
        index: The MinSearch index to search.
        filter_dict (dict, optional): Dictionary of filters.
        boost (dict, optional): Dictionary of boost values.
        num_results (int, optional): Number of results to return.
        Default is 5.

    Returns:
        list: Search results.
    """
    if not boost:
        boost = {}

    if not filter_dict:
        filter_dict = {}

    results = index.search(
        query=query, filter_dict=filter_dict, boost_dict=boost, num_results=num_results
    )

    return results


def build_context(search_results):
    """
    Build context from search results.

    Args:
        search_results (list): List of search results.

    Returns:
        str: A formatted string of the search results.
    """
    context = ""

    for doc in search_results:
        context = (
            context
            + f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}\n\n"
        )

    return context


def build_prompt(prompt_template_path, document_dict):
    """
    Build a prompt from a template and document dictionary.

    Args:
        prompt_template_path (str): Path to the prompt template.
        document_dict (dict): Dictionary of document parameters.

    Returns:
        str: The formatted prompt.

    Raises:
        WrongPomptParams: If the document dictionary does not
        match the expected parameters in the template.
    """
    with open(prompt_template_path, "r", encoding="utf-8") as f:
        prompt_template = f.read().strip()

    expected_params = sorted(find_parameters(prompt_template))
    provided_params = sorted(list(document_dict.keys()))

    if not is_sublist(main_list=provided_params, sublist=expected_params):
        raise WrongPomptParams(
            f"Expected presence of {expected_params}, but got {provided_params}"
        )

    prompt = prompt_template.format(**document_dict)

    return prompt


def llm(client, prompt, model_name="gpt-4o", generate_params=None):
    """
    Generate a response using a language model.

    Args:
        client: The client instance to use for generating responses.
        prompt (str): The prompt to send to the model.
        model_name (str, optional): The name of the model to use.
        Default is 'gpt-4o'.
        generate_params (dict, optional): Additional parameters
        for generation.

    Returns:
        str: The generated response.
    """
    if not generate_params:
        generate_params = {}

    if model_name in ["gpt-4o", "phi3"]:
        response = client.chat.completions.create(
            model=model_name, messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content

    elif model_name == "google/flan-t5-small":
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        llm_model = T5ForConditionalGeneration.from_pretrained(
            model_name, device_map="auto"
        )

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

    else:
        raise ModelNotCached(
            f"`model_name`='{model_name}' is not previously cached, 'gpt-4o', or None"
        )

    return result


def rag(**kwargs):
    """
    Perform Retrieval-Augmented Generation (RAG).

    Args:
        **kwargs: Arbitrary keyword arguments including query,
        search_context, index, es_client, index_name, filter_dict,
        boost, num_results, prompt_template_path, client,
        model_name, and generate_params.

    Returns:
        str: The generated answer.

    Raises:
        SearchContextWrongValueError: If search_context is invalid.
    """
    query = kwargs.get("query")
    search_context = kwargs.get("search_context", "minsearch")

    if search_context == "minsearch":
        search_results = search(
            query=query,
            index=kwargs.get("index"),
            filter_dict=kwargs.get("filter_dict"),
            boost=kwargs.get("boost"),
            num_results=kwargs.get("num_results"),
        )
    elif search_context == "elasticsearch":
        search_results = elastic_search(
            query=query,
            es_client=kwargs.get("es_client"),
            index_name=kwargs.get("index_name"),
            filter_dict=kwargs.get("filter_dict"),
            boost=kwargs.get("boost"),
            num_results=kwargs.get("num_results"),
        )
    else:
        raise SearchContextWrongValueError(
            "Parameter `search_context` value must be in ['minsearch', 'elasticsearch'] or None"
        )

    context = build_context(search_results)
    document_dict = {"question": query, "context": context}

    prompt = build_prompt(
        kwargs.get("prompt_template_path"), document_dict=document_dict
    )
    answer = llm(
        client=kwargs.get("client"),
        prompt=prompt,
        model_name=kwargs.get("model_name"),
        generate_params=kwargs.get("generate_params", {}),
    )
    return answer
