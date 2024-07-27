from tqdm.auto import tqdm

from exceptions.exceptions import (
    SearchContextWrongValueError,
    QueryTypeWrongValueError,
)

from utils.ollama import get_embedding


def calculate_relevance(
    df_ground_truth,
    search_callable,
    search_callable_params,
    search_context='elasticsearch',
    query_type='text',
):
    relevance_total = []

    if 'model_name' in search_callable_params:
        model_name = search_callable_params.pop('model_name')
    if 'client' in search_callable_params:
        client = search_callable_params.pop('client')

    for q in tqdm(
        df_ground_truth.to_dict(orient='records')
    ):
        doc_id = q['document']
        filter_dict = {'course': q['course']}

        if query_type not in ['text', 'vector']:
            raise QueryTypeWrongValueError(
                "Parameter `query_type` value must be in ['text', 'vector'] or None"
            )
        
        if search_context not in ['elasticsearch', 'minsearch']:
            raise SearchContextWrongValueError(
                "Parameter `search_context` value must be in ['minsearch', 'elasticsearch'] or None"
            )

        if search_context == 'elasticsearch' and query_type == 'vector':
            query_vector = get_embedding(
                client=client, text=q['question'], model_name=model_name
            )

            results = search_callable(
                query_vector=query_vector,
                filter_dict=filter_dict,
                **search_callable_params,
            )

        else:
            results = search_callable(
                query=q['question'],
                filter_dict=filter_dict,
                **search_callable_params,
            )

        relevance = [d['id'] == doc_id for d in results]
        relevance_total.append(relevance)

    return relevance_total


def hit_rate(relevance_total):
    cnt = 0

    for line in relevance_total:
        if True in line:
            cnt = cnt + 1

    return cnt / len(relevance_total)


def mrr(relevance_total):
    total_score = 0.0

    for line in relevance_total:
        for rank in range(len(line)):
            if line[rank] == True:
                total_score = total_score + 1 / (rank + 1)

    return total_score / len(relevance_total)