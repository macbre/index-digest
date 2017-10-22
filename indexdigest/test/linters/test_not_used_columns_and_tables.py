from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.not_used_columns_and_tables import check_not_used_tables
from indexdigest.database import Database
from indexdigest.test import DatabaseTestMixin


class LimitedViewDatabase(Database, DatabaseTestMixin):
    """
    Limit test to tables from sql/0006-not-used-columns-and-tables.sql
    """
    def get_tables(self):
        return ['0006_not_used_columns', '0006_not_used_tables']


class TestNotUsedTables(TestCase):

    @property
    def connection(self):
        return LimitedViewDatabase.connect_dsn(DatabaseTestMixin.DSN)

    def test_not_used_tables(self):
        with open('sql/0006-not-used-columns-and-tables-log') as fp:
            queries = fp.readlines()

        reports = check_not_used_tables(database=self.connection, queries=queries)

        print(reports)

        self.assertEqual(len(reports), 1)
        self.assertEqual(str(reports[0]), '0006_not_used_tables: Table was not used by provided queries')
        self.assertEqual(reports[0].table_name, '0006_not_used_tables')

        # assert False
