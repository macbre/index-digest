"""
This linter checks for ...
"""
from collections import defaultdict

from indexdigest.utils import LinterEntry

# skip small tables
ROWS_COUNT_THRESHOLD = 1000


def check_low_cardinality_index(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list[LinterEntry]
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
            " TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = '{database_name}'".
            format(table_name=table_name, database_name=database.db_name)
        )

        for index in indices:
            print(table_name, rows_count, index)
        assert False

"""
    yield LinterEntry(linter_type='low_cardinality_index', table_name=table_name,
                      message='"{}" ...'.
                      format("foo"),
                      context={"foo": str("bar")})
"""
