"""
This linter checks for too high offset SELECT queries
"""
from collections import OrderedDict

from sql_metadata import get_query_limit_and_offset, get_query_tables

from indexdigest.utils import LinterEntry, shorten_query, is_select_query


OFFSET_THRESHOLD = 1000


def check_high_offset_selects(_, queries):
    """
    :type _ indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    for query in queries:
        # ignore insert queries (#140)
        if not is_select_query(query):
            continue

        res = get_query_limit_and_offset(query)

        if res is None:
            continue

        (limit, offset) = res

        if offset < OFFSET_THRESHOLD:
            continue

        table_name = get_query_tables(query)[0]

        context = OrderedDict()
        context['query'] = query
        context['limit'] = limit
        context['offset'] = offset

        yield LinterEntry(linter_type='high_offset_selects', table_name=table_name,
                          message='"{}" query uses too high offset impacting the performance'.
                          format(shorten_query(query)),
                          context=context)
