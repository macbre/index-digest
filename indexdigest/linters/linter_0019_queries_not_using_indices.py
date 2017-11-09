"""
This linter checks SELECT queries that do not use indices
"""
from collections import OrderedDict

from indexdigest.utils import LinterEntry, explain_queries, shorten_query


def check_queries_not_using_indices(database, queries):
    """
    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    for (query, table_used, index_used, explain_row) in explain_queries(database, queries):
        # print(query, explain_row)

        # EXPLAIN can return no matching row in const table in Extra column.
        # Do not consider this query as not using an index. -- see #44
        if explain_row['Extra'] in [
                'Impossible WHERE noticed after reading const tables',
                'no matching row in const table',
        ]:
            continue

        if index_used is None:
            context = OrderedDict()
            context['query'] = query

            # https://dev.mysql.com/doc/refman/5.7/en/explain-output.html#explain-extra-information
            context['explain_extra'] = explain_row['Extra']
            context['explain_rows'] = explain_row['rows']
            context['explain_filtered'] = explain_row.get('filtered')  # can be not set
            context['explain_possible_keys'] = explain_row['possible_keys']

            yield LinterEntry(linter_type='queries_not_using_index', table_name=table_used,
                              message='"{}" query did not make use of any index'.
                              format(shorten_query(query)),
                              context=context)
