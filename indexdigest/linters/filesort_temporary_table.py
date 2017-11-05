"""
This linter checks for SELECT queries whether they trigger filesort or temporary file
"""
from collections import OrderedDict

from indexdigest.utils import explain_queries, LinterEntry


def filter_explain_extra(database, queries, check):
    """
    Parse "Extra" column from EXPLAIN query results, e.g.

    "Using where; Using temporary; Using filesort"

    :type database  indexdigest.database.Database
    :type queries list[str]
    :type check str
    :rtype: list
    """
    for (query, table_used, _, explain_row) in explain_queries(database, queries):
        extra_parsed = str(explain_row['Extra']).split('; ')

        if check in extra_parsed:
            context = OrderedDict()
            context['query'] = query

            context['explain_extra'] = explain_row['Extra']
            context['explain_rows'] = explain_row['rows']
            context['explain_filtered'] = explain_row.get('filtered')  # can be not set
            context['explain_possible_keys'] = explain_row['possible_keys']

            yield (query, table_used, context)


def check_queries_using_filesort(database, queries):
    """
    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    reports = []
    filtered = filter_explain_extra(database, queries, check='Using filesort')

    for (query, table_used, context) in filtered:
        reports.append(
            LinterEntry(linter_type='queries_using_filesort', table_name=table_used,
                        message='"{}" query used filesort'.
                        format('{}...'.format(query[:50]) if len(query) > 50 else query),
                        context=context))

    return reports
