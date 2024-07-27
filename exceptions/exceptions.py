class ElasticsearchError(Exception):
    """Base class for all Elasticsearch-related exceptions."""
    pass

class ElasticsearchConnectionError(ElasticsearchError):
    """Exception raised for errors in establishing a connection to Elasticsearch."""
    pass

class ElasticsearchQueryError(ElasticsearchError):
    """Exception raised for errors in querying Elasticsearch."""
    pass

class SearchContextWrongValueError(Exception):
    """Ensure that search_context is defined (either minsearch or elasticseach)"""
    pass

class QueryTypeWrongValueError(Exception):
    """Ensure that query_type is defined (either text or vector)"""
    pass

class WrongPomptParams(Exception):
    """Ensure that the params passed to the prompt template are the expected params"""
    pass