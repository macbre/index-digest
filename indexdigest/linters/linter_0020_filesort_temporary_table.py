"""
This linter checks for SELECT queries whether they trigger filesort or temporary file
"""
from collections import OrderedDict

from indexdigest.utils import explain_queries, LinterEntry, shorten_query


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
            context['explain_key'] = explain_row['key']

            yield (query, table_used, context)


def check_queries_using_filesort(database, queries):
    """
    Using filesort

    MySQL must do an extra pass to find out how to retrieve the rows in sorted order. The sort is
    done by going through all rows according to the join type and storing the sort key and pointer
    to the row for all rows that match the WHERE clause. The keys then are sorted and the rows are
    retrieved in sorted order.

    Percona says: The truth is, filesort is badly named. Anytime a sort can't be performed from an
    index, it's a filesort. It has nothing to do with files. Filesort should be called "sort."
    It is quicksort at heart.

    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    filtered = filter_explain_extra(database, queries, check='Using filesort')

    for (query, table_used, context) in filtered:
        yield LinterEntry(linter_type='queries_using_filesort', table_name=table_used,
                          message='"{}" query used filesort'.format(shorten_query(query)),
                          context=context)


def check_queries_using_temporary(database, queries):
    """
    Using temporary

    To resolve the query, MySQL needs to create a temporary table to hold the result. This
    typically happens if the query contains GROUP BY and ORDER BY clauses that list columns
    differently.

    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    filtered = filter_explain_extra(database, queries, check='Using temporary')

    for (query, table_used, context) in filtered:
        yield LinterEntry(linter_type='queries_using_temporary', table_name=table_used,
                          message='"{}" query used temporary'.format(shorten_query(query)),
                          context=context)
