"""
This linter reports tables with just a single column
"""
from indexdigest.utils import LinterEntry


def check_single_column(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list[LinterEntry]
    """
    tables = [
        table
        for table in database.get_tables()
        if len(database.get_table_columns(table)) == 1
    ]

    for table in tables:
        yield LinterEntry(linter_type='single_column', table_name=table,
                          message='"{}" has just a single column'.
                          format(table),
                          context={'schema': database.get_table_schema(table)})
