"""
This linter checks for ...
"""
from collections import OrderedDict

from indexdigest.utils import LinterEntry

# skip small tables
ROWS_COUNT_THRESHOLD = 100000

# cardinality threshold
INDEX_CARDINALITY_THRESHOLD = 6

# the least frequent value should be used at most by x% rows
INDEX_VALUE_PERCENTAGE_THRESHOLD = 20


def get_low_cardinality_indices(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list
    """
    for table_name in database.get_tables():
        rows_count = database.get_table_rows_estimate(table_name)
        if rows_count < ROWS_COUNT_THRESHOLD:
            continue

        # get table indices statistics
        # @see https://dev.mysql.com/doc/refman/5.7/en/show-index.html
        # @see https://www.percona.com/blog/2007/08/28/do-you-always-need-index-on-where-column/
        indices = database.query_dict_rows(
            "select TABLE_NAME, INDEX_NAME, COLUMN_NAME, CARDINALITY from"
            " INFORMATION_SCHEMA.STATISTICS where"
            " TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = '{database_name}'".format(
                table_name=table_name, database_name=database.db_name)
        )

        for index in indices:
            # the cardinality is too high
            if index['CARDINALITY'] > INDEX_CARDINALITY_THRESHOLD:
                continue

            yield table_name, rows_count, index


def check_low_cardinality_index(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list[LinterEntry]
    """
    for table_name, rows_count, index in get_low_cardinality_indices(database):
        # the least frequent value should be used in up to 20% of rows
        # https://www.percona.com/blog/2007/08/28/do-you-always-need-index-on-where-column/
        row = database.query_dict_row(
            'SELECT {column} AS value, COUNT(*) AS cnt FROM `{table}` '
            'GROUP BY 1 ORDER BY 2 ASC LIMIT 1'.format(
                column=index['COLUMN_NAME'], table=index['TABLE_NAME']
            )
        )

        value_usage = 100. * row['cnt'] / rows_count
        # print(row, value_usage)

        # the least frequent value is quite rare - it makes sense to have an index here
        if value_usage < INDEX_VALUE_PERCENTAGE_THRESHOLD:
            continue

        # print(value_usage, index, table_name)

        context = OrderedDict()
        context['column_name'] = index['COLUMN_NAME']
        context['index_name'] = index['INDEX_NAME']
        context['index_cardinality'] = int(index['CARDINALITY'])
        context['schema'] = database.get_table_schema(table_name)
        context['value_usage'] = value_usage

        yield LinterEntry(linter_type='low_cardinality_index', table_name=table_name,
                          message='"{}" index on "{}" column has low cardinality, '
                                  'check if it is needed'.
                          format(index['INDEX_NAME'], index['COLUMN_NAME']),
                          context=context)
