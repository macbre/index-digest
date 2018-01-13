"""
This linter checks for select queries with * wildcard
"""
from sql_metadata import preprocess_query, get_query_tables, get_query_tokens, Wildcard

from indexdigest.utils import LinterEntry, shorten_query, is_select_query


def is_wildcard_query(query):
    """
    Checks if provided query selects using a * wildcard
    :type query str
    :rtype bool
    """
    if not is_select_query(query):
        return False

    query = preprocess_query(query)
    tokens = get_query_tokens(query)

    last_token = None

    for token in tokens:
        if token.ttype is Wildcard:
            # print([query, token, 'last token', last_token])

            # check what was before the wildcard
            # count(*) ?
            if last_token and str(last_token) not in ['(']:
                return True
        else:
            last_token = token

    return False


def check_select_star(_, queries):
    """
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    queries_with_wildcard = [
        query for query in queries
        if is_wildcard_query(query)
    ]

    for query in queries_with_wildcard:
        table_name = get_query_tables(query)[0]

        yield LinterEntry(linter_type='select_star', table_name=table_name,
                          message='"{}" query uses SELECT *'.
                          format(shorten_query(query)),
                          context={"query": query})
