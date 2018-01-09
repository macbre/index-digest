"""
This linter checks for empty tables
"""
from indexdigest.utils import LinterEntry


def check_empty_tables(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list[LinterEntry]
    """
    empty_tables = [
        table for table in database.get_tables()
        # use both "information_schema" and "explain select count(*)" based methods
        # to get the rows count estimate
        if database.get_table_metadata(table).get('rows') == 0
        or database.get_table_rows_estimate(table) == 0
    ]

    for table in empty_tables:
        yield LinterEntry(linter_type='empty_tables', table_name=table,
                          message='"{}" table has no rows, is it really needed?'.format(table),
                          context={'schema': database.get_table_schema(table)})
