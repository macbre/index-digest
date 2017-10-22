"""
This linter checks for not used columns and tables by going through SELECT queries
"""
from collections import defaultdict

from indexdigest.utils import LinterEntry, is_select_query


def check_not_used_columns_and_tables(database, queries):
    """
    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    reports = []

    # get database meta-data
    tables = database.get_tables()
    columns = {}

    for table in database.get_tables():
        columns[table] = database.get_table_metadata(table)['columns']

    # analyze only SELECT queries from the log
    queries = filter(is_select_query, queries)

    used_columns = defaultdict(list)
    used_tables = set()

    for query in queries:
        res = database.explain_query(query)
        print(query, columns, list(res))

    """
        indices = database.get_table_indices(table)
        for (redundant_index, suggested_index) in get_redundant_indices(indices):
            reports.append(
                LinterEntry(linter_type='redundant_indices', table_name=table,
                            message='{} index can be removed as redundant (covered by {})'.
                            format(redundant_index, suggested_index),
                            context={'redundant': redundant_index, 'covered_by': suggested_index}))
    """

    print(list(queries))
    print(list(tables))
    print(columns)

    return reports
