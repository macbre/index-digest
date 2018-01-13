"""
This linter checks for select queries with HAVING clause
"""
from sqlparse.tokens import Keyword
from sql_metadata import preprocess_query, get_query_tables, get_query_tokens

from indexdigest.utils import LinterEntry, shorten_query, is_select_query


def query_has_having_clause(query):
    """
    Checks if provided query uses HAVING clause
    :type query str
    :rtype bool
    """
    if not is_select_query(query):
        return False

    query = preprocess_query(query)
    tokens = get_query_tokens(query)

    for token in tokens:
        if token.ttype is Keyword and str(token).upper() == 'HAVING':
            return True

    return False


def check_having_clause(_, queries):
    """
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    queries_with_having_clause = [
        query for query in queries
        if query_has_having_clause(query)
    ]

    for query in queries_with_having_clause:
        table_name = get_query_tables(query)[0]

        yield LinterEntry(linter_type='having_clause', table_name=table_name,
                          message='"{}" query uses HAVING clause'.
                          format(shorten_query(query)),
                          context={"query": query})
