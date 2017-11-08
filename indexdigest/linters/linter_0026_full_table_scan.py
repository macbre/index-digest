"""
This linter checks for SELECT queries that use full table scan
"""
from collections import OrderedDict

from indexdigest.utils import explain_queries, LinterEntry, shorten_query


def check_full_table_scan(database, queries):
    """
    Full table scan

    An operation that requires reading the entire contents of a table, rather than just selected
    portions using an index. Typically performed either with small lookup tables, or in data
    warehousing situations with large tables where all available data is aggregated and analyzed.
    How frequently these operations occur, and the sizes of the tables relative to available memory,
    have implications for the algorithms used in query optimization and managing the buffer pool.

    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    for (query, table_used, _, row) in explain_queries(database, queries):
        # The output from EXPLAIN shows ALL in the type column when
        # MySQL uses a full table scan to resolve a query.
        if row['type'] != 'ALL':
            continue

        context = OrderedDict()
        context['query'] = query
        context['explain_rows'] = row['rows']

        yield LinterEntry(linter_type='queries_using_full_table_scan', table_name=table_used,
                          message='"{}" query triggered full table scan'.
                          format(shorten_query(query)),
                          context=context)
