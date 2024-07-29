"""
This module provides functions to calculate relevance metrics for 
search results.
It includes functions to calculate the relevance of search results 
against ground truth data, as well as hit rate and 
mean reciprocal rank (MRR) metrics.
"""

from tqdm.auto import tqdm

from exceptions.exceptions import (QueryTypeWrongValueError,
                                   SearchContextWrongValueError)
from utils.ollama import get_embedding

from utils.query import (build_prompt,
                         llm)

from utils.utils import parse_json_response

def calculate_relevance(
    df_ground_truth,
    search_callable,
    search_callable_params,
    search_context="elasticsearch",
    query_type="text",
):
    """
    Calculate the relevance of search results against ground
    truth data.

    Args:
        df_ground_truth (pandas.DataFrame): DataFrame containing
        ground truth data with columns 'document' and 'course'.
        
        index_name (str, optional): Name of the Elasticsearch index.
        Required if search_context is 'elasticsearch'.
        
        es_client (Elasticsearch, optional): Elasticsearch client
        instance. Required if search_context is 'elasticsearch'.
        
        boost (dict, optional): Dictionary of boost values for
        specific fields.
        
        num_results (int, optional): Number of search results to
        return. Default is 5.
        
        search_context (str, optional): The search context to use
        ('elasticsearch' or 'minsearch'). Default is 'elasticsearch'.
        
        index (optional): Index object for minsearch. Required if
        search_context is 'minsearch'.

    Returns:
        list: A list of lists where each inner list contains boolean
        values indicating relevance of search results.
    """
    relevance_total = []

    if "model_name" in search_callable_params:
        model_name = search_callable_params.pop("model_name")
    else:
        assert (
            query_type == "text"
        ), "`query_type` must be 'text', if no OpenAI client is passed."
    if "client" in search_callable_params:
        client = search_callable_params.pop("client")
    else:
        assert (
            query_type == "text"
        ), "`query_type` must be 'text', if no OpenAI client is passed."

    if query_type not in ["text", "vector"]:
        raise QueryTypeWrongValueError(
            "Parameter `query_type` value must be in ['text', 'vector'] or None"
        )

    if search_context not in ["elasticsearch", "minsearch"]:
        raise SearchContextWrongValueError(
            "Parameter `search_context` value must be in ['minsearch', 'elasticsearch'] or None"
        )

    for q in tqdm(df_ground_truth.to_dict(orient="records")):
        doc_id = q["document"]
        filter_dict = {"course": q["course"]}

        if search_context == "elasticsearch" and query_type == "vector":
            query_vector = get_embedding(
                client=client, text=q["question"], model_name=model_name
            )

            results = search_callable(
                query_vector=query_vector,
                filter_dict=filter_dict,
                **search_callable_params,
            )

        else:
            results = search_callable(
                query=q["question"],
                filter_dict=filter_dict,
                **search_callable_params,
            )

        relevance = [d["id"] == doc_id for d in results]
        relevance_total.append(relevance)

    return relevance_total


def hit_rate(relevance_total):
    """
    Calculate the hit rate from relevance results.

    Args:
        relevance_total (list): A list of lists where each inner
        list contains boolean values indicating relevance of
        search results.

    Returns:
        float: The hit rate, calculated as the proportion of queries
        with at least one relevant result.
    """
    cnt = 0

    for line in relevance_total:
        if True in line:
            cnt = cnt + 1

    return cnt / len(relevance_total)


def mrr(relevance_total):
    """
    Calculate the mean reciprocal rank (MRR) from relevance results.

    Args:
        relevance_total (list): A list of lists where each inner
        list contains boolean values indicating relevance of
        search results.

    Returns:
        float: The mean reciprocal rank, calculated as the average
        of reciprocal ranks of the first relevant result for each
        query.
    """
    total_score = 0.0

    for line in relevance_total:
        for rank, _ in enumerate(line):
            if line[rank] is True:
                total_score = total_score + 1 / (rank + 1)

    return total_score / len(relevance_total)


def llm_as_a_judge(
    client,
    prompt_template_path,
    df_to_judge,
    model_name="gpt-3.5-turbo",
):
    results = []
    
    for record in tqdm(df_to_judge.to_dict(orient='records')):
        prompt = build_prompt(
            prompt_template_path,
            **record,
        )
        
        response = llm(client, prompt, model_name)
        response = parse_json_response(response)
        
        results.append(response)
        
    return results
