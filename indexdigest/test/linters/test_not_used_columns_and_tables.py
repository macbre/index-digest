from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.not_used_columns_and_tables import check_not_used_tables, check_not_used_columns, \
    get_used_tables_from_queries
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
        self.assertEqual(str(reports[0]), '0006_not_used_tables: "0006_not_used_tables" table was not used by provided queries')
        self.assertEqual(reports[0].table_name, '0006_not_used_tables')

    def test_get_used_tables_from_queries(self):
        with open('sql/0006-not-used-columns-and-tables-log') as fp:
            queries = fp.readlines()

        tables = get_used_tables_from_queries(database=self.connection, queries=queries)

        print(tables)

        self.assertListEqual(tables, ['0006_not_used_columns'])

        # assert False


class TestNotUsedColumns(TestCase):

    @property
    def connection(self):
        return LimitedViewDatabase.connect_dsn(DatabaseTestMixin.DSN)

    def test_not_used_columns(self):
        queries = [
            'SELECT test, id FROM `0006_not_used_columns` WHERE foo = "a"'
        ]

        reports = check_not_used_columns(database=self.connection, queries=queries)

        self.assertEqual(len(reports), 1)
        self.assertEqual(str(reports[0]), '0006_not_used_columns: "bar" column was not used by provided queries')
        self.assertEqual(reports[0].table_name, '0006_not_used_columns')
        self.assertEqual(reports[0].context['column_name'], 'bar')
        self.assertEqual(reports[0].context['column_type'], 'varchar')

        # assert False

    def test_not_used_columns_two(self):
        queries = [
            'SELECT test FROM `0006_not_used_columns` WHERE foo = "a"'
        ]

        reports = check_not_used_columns(database=self.connection, queries=queries)

        # reports ordered is the same as schema columns order
        self.assertEqual(len(reports), 2)
        self.assertEqual(reports[0].context['column_name'], 'id')
        self.assertEqual(reports[1].context['column_name'], 'bar')

        # assert False
