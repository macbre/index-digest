"""
This linter checks for not used columns and tables by going through SELECT queries
"""
import logging

from collections import defaultdict

from indexdigest.utils import LinterEntry, is_select_query
from indexdigest.query import get_query_columns, get_query_tables


def get_used_tables_from_queries(database, queries):
    """
    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[str]
    """
    used_tables = []
    queries = filter(is_select_query, queries)

    for query in queries:
        # run EXPLAIN for each query from the log
        for row in database.explain_query(query):
            if 'table' in row:
                used_tables.append(row['table'])

    return list(set(used_tables))  # make it unique


def check_not_used_tables(database, queries):
    """
    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    logger = logging.getLogger(__name__)

    # get database meta-data
    tables = database.get_tables()

    # analyze only SELECT queries from the log
    used_tables = get_used_tables_from_queries(database, queries)
    logger.info("These tables were used by provided queries: %s", used_tables)

    # now check which tables were not used
    not_used_tables = [table for table in tables if table not in used_tables]

    # generate reports
    reports = []
    for table in not_used_tables:
        reports.append(
            LinterEntry(linter_type='not_used_tables', table_name=table,
                        message='"{}" table was not used by provided queries'.format(table)))

    return reports


def check_not_used_columns(database, queries):
    """
    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    :raises Exception
    """
    logger = logging.getLogger(__name__)

    # analyze only SELECT queries from the log
    queries = list(filter(is_select_query, queries))

    used_tables = get_used_tables_from_queries(database, queries)
    used_columns = defaultdict(list)

    logger.info("Will check these tables: %s", used_tables)

    # analyze given queries and collect used columns for each table
    for query in queries:
        # FIXME: assume we're querying just a single table for now
        table = get_query_tables(query)[0]
        columns = get_query_columns(query)

        # print(query, table, columns)

        # add used columns per table
        used_columns[table] += columns

    # analyze table schemas and report not used columns for each table
    reports = []

    for table in used_tables:
        logger.info("Checking %s table", table)
        table_columns = database.get_table_metadata(table)['columns']

        # now get the difference and report them
        not_used_columns = [
            column for column in table_columns.keys()
            if column not in set(used_columns[table])
        ]

        for column in not_used_columns:
            reports.append(
                LinterEntry(linter_type='not_used_columns', table_name=table,
                            message='"{}" column was not used by provided queries'.format(column),
                            context={'column_name': column, 'column_type': table_columns[column]}))

    return reports
