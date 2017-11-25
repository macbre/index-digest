"""
This linter checks SELECT queries that use LIKE '%foo' conditions
"""
import re

from collections import OrderedDict

from indexdigest.utils import LinterEntry, explain_queries, shorten_query


def query_uses_leftmost_like(query):
    """
    Returns True for queries with LIKE '%foo' conditions

    :type query str
    :rtype: bool
    """
    # quit fast
    if 'like' not in query.lower():
        return False

    matches = re.search(r'LIKE\s\s?[\'"]%\w', query, flags=re.IGNORECASE)
    return matches is not None


def check_selects_with_like(database, queries):
    """
    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    for (query, table_used, index_used, explain_row) in explain_queries(database, queries):
        if index_used is None and query_uses_leftmost_like(query):
            context = OrderedDict()
            context['query'] = query

            # https://dev.mysql.com/doc/refman/5.7/en/explain-output.html#explain-extra-information
            context['explain_extra'] = explain_row['Extra']
            context['explain_rows'] = explain_row['rows']

            yield LinterEntry(linter_type='selects_with_like', table_name=table_used,
                              message='"{}" query uses LIKE with left-most wildcard'.
                              format(shorten_query(query)),
                              context=context)
