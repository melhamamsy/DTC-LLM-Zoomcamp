from tqdm.auto import tqdm
from utils.elasticsearch import elastic_search
from exceptions.exceptions import SearchContextWrongValueError
from utils.query import search


def calculate_relevance(
    df_ground_truth,
    index_name=None,
    es_client=None,
    boost=None,
    num_results=5,
    search_context='elasticsearch',
    index=None,
):
    relevance_total = []
    for q in tqdm(
        df_ground_truth.to_dict(orient='records')
    ):
        doc_id = q['document']
        filter_dict = {'course': q['course']}

        if search_context == 'elasticsearch':
            results = elastic_search(
                es_client=es_client, 
                index_name=index_name, 
                query=q['question'], 
                filter_dict=filter_dict,
                boost=boost,
                num_results=num_results,
            )
        elif search_context == 'minsearch':
            results = search(
                query=q['question'], 
                index=index, 
                filter_dict=filter_dict, 
                boost=boost, 
                num_results=num_results,
            )
        else:
            raise SearchContextWrongValueError(
                "Parameter `search_context` value must be in ['minsearch', 'elasticsearch'] or None"
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