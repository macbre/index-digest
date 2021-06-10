from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0006_not_used_columns_and_tables import check_not_used_tables, check_not_used_columns, \
    get_used_tables_from_queries
from indexdigest.database import Database
from indexdigest.test import DatabaseTestMixin, read_queries_from_log


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
        reports = list(check_not_used_tables(
            database=self.connection, queries=read_queries_from_log('0006-not-used-columns-and-tables-log')))

        print(reports)

        self.assertEqual(len(reports), 1)
        self.assertEqual(str(reports[0]), '0006_not_used_tables: "0006_not_used_tables" table was not used by provided queries')
        self.assertEqual(reports[0].table_name, '0006_not_used_tables')

        assert str(reports[0].context['schema']).startswith('CREATE TABLE `0006_not_used_tables` (\n')

        # these are estimates, can't assert a certain value
        assert reports[0].context['table_size_mb'] > 0.0001
        assert reports[0].context['rows_estimated'] > 0

    def test_get_used_tables_from_queries(self):
        queries = [
            'SELECT /* a comment */ foo FROM `0006_not_used_columns` AS r WHERE item_id = 1;',  # table alias
            'SELECT 1 FROM `0006_not_used_tables` WHERE item_id = 3;',
        ]

        tables = get_used_tables_from_queries(queries)

        print(tables)

        self.assertListEqual(tables, ['0006_not_used_columns', '0006_not_used_tables'])

        # assert False


class TestNotUsedColumns(TestCase):

    @property
    def connection(self):
        return LimitedViewDatabase.connect_dsn(DatabaseTestMixin.DSN)

    def test_not_used_columns(self):
        queries = [
            'SELECT test, item_id FROM `0006_not_used_columns` WHERE foo = "a"'
        ]

        reports = list(check_not_used_columns(database=self.connection, queries=queries))

        self.assertEqual(len(reports), 1)
        self.assertEqual(str(reports[0]), '0006_not_used_columns: "bar" column was not used by provided queries')
        self.assertEqual(reports[0].table_name, '0006_not_used_columns')
        self.assertEqual(reports[0].context['column_name'], 'bar')
        self.assertEqual(reports[0].context['column_type'], 'varchar(16)')

        # assert False

    def test_not_used_columns_two(self):
        queries = [
            'SELECT test FROM `0006_not_used_columns` WHERE foo = "a"'
        ]

        reports = list(check_not_used_columns(database=self.connection, queries=queries))

        # reports ordered is the same as schema columns order
        self.assertEqual(len(reports), 2)
        self.assertEqual(reports[0].context['column_name'], 'item_id')
        self.assertEqual(reports[0].context['column_type'], 'int')
        self.assertEqual(reports[1].context['column_name'], 'bar')
        self.assertEqual(reports[1].context['column_type'], 'varchar(16)')

        # assert False

    def test_parsing_errors_handling(self):
        queries = [
            'SELECT test',
            'SELECT 0020_big_table t WHERE id BETWEEN 10 AND 20 GROUP BY val'
        ]

        reports = list(check_not_used_columns(database=self.connection, queries=queries))
        self.assertEqual(len(reports), 0)

        # assert False
