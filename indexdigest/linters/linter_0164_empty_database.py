"""
This linter checks for databases with no tables
"""
from indexdigest.utils import LinterEntry


def get_empty_databases(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list[str]
    """
    for db_name in database.query_list('SHOW DATABASES'):
        # skip "core" MySQL databases
        if db_name in ['information_schema']:
            continue

        tables_count = database.query_field('SELECT COUNT(*) FROM information_schema.TABLES '
                                            'WHERE TABLE_SCHEMA = "{}" AND '
                                            'TABLE_TYPE = "BASE TABLE"'.format(db_name))
        # print(db_name, tables_count)
        if tables_count == 0:
            yield db_name


def check_empty_database(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list[LinterEntry]
    """
    for db_name in get_empty_databases(database):
        yield LinterEntry(linter_type='empty_database', table_name=db_name,
                          message='"{}" database has no tables'.format(db_name))
