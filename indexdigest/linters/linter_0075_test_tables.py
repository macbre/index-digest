"""
This linter reports tables with "test" word in their name
"""
import re

from indexdigest.utils import LinterEntry

TEST_TABLES = (
    'test',
    'temp',
)


def is_test_table(table_name):
    """
    :type table_name str
    :rtype: bool
    """
    return re.search(r'(^|_)({})(_|$)'.format('|'.join(TEST_TABLES)), table_name) is not None


def check_test_tables(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list[LinterEntry]
    """
    test_tables = [
        table for table in database.get_tables()
        if is_test_table(table)
    ]

    for table in test_tables:
        yield LinterEntry(linter_type='test_tables', table_name=table,
                          message='"{}" seems to be a test table'.
                          format(table),
                          context={'schema': database.get_table_schema(table)})
