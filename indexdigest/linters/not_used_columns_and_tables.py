"""
This linter checks for not used columns and tables by going through SELECT queries
"""
from indexdigest.utils import LinterEntry, is_select_query


def check_not_used_tables(database, queries):
    """
    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """

    # get database meta-data
    tables = database.get_tables()

    # analyze only SELECT queries from the log
    queries = filter(is_select_query, queries)

    used_tables = set()

    for query in queries:
        # run EXPLAIN for each query from the log
        for row in database.explain_query(query):
            if 'table' in row:
                used_tables.add(row['table'])

    # now check which tables were not used
    not_used_tables = filter(
        lambda t: t not in used_tables,
        tables
    )

    # generate reports
    reports = []
    for table in not_used_tables:
        reports.append(
            LinterEntry(linter_type='not_used_tables', table_name=table,
                        message='Table was not used by provided queries'))

    return reports
