"""
This linter checks for not used columns and tables by going through SELECT queries
"""
import logging

from collections import defaultdict, OrderedDict
from sql_metadata import get_query_columns, get_query_tables

from indexdigest.utils import LinterEntry, is_select_query


def get_used_tables_from_queries(queries):
    """
    :type queries list[str]
    :rtype: list[str]
    """
    used_tables = []
    queries = filter(is_select_query, queries)

    for query in queries:
        # parse each query from the log
        tables = get_query_tables(query)
        if tables and tables[0] not in used_tables:
            used_tables.append(tables[0])

    return used_tables


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
    used_tables = get_used_tables_from_queries(queries)
    logger.info("These tables were used by provided queries: %s", used_tables)

    # now check which tables were not used
    not_used_tables = [table for table in tables if table not in used_tables]

    # generate reports
    for table in not_used_tables:
        metadata = database.get_table_metadata(table)
        context = OrderedDict()

        context['schema'] = database.get_table_schema(table)
        context['table_size_mb'] = \
            1. * (metadata['data_size'] + metadata['index_size']) / 1024 / 1024
        context['rows_estimated'] = database.get_table_rows_estimate(table)

        yield LinterEntry(linter_type='not_used_tables', table_name=table,
                          message='"{}" table was not used by provided queries'.format(table),
                          context=context)


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

    used_tables = get_used_tables_from_queries(queries)
    used_columns = defaultdict(list)

    logger.info("Will check these tables: %s", used_tables)

    # analyze given queries and collect used columns for each table
    for query in queries:
        tables = get_query_tables(query)
        if tables:
            columns = get_query_columns(query)

            # print(query, table, columns)

            # add used columns per table
            # FIXME: assume we're querying just a single table for now
            used_columns[tables[0]] += columns
        else:
            logger.error('Unable to extract tables and columns used from the query: %s',
                         query)

    # analyze table schemas and report not used columns for each table
    for table in used_tables:
        logger.info("Checking %s table", table)
        table_columns = database.get_table_columns(table)

        # now get the difference and report them
        not_used_columns = [
            column for column in table_columns
            if column.name not in set(used_columns[table])
        ] if table_columns else []

        for column in not_used_columns:
            yield LinterEntry(linter_type='not_used_columns', table_name=table,
                              message='"{}" column was not used by provided queries'.format(column),
                              context={'column_name': column.name, 'column_type': column.type})
