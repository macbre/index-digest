from __future__ import print_function

from unittest import TestCase

from indexdigest.linters import check_latin_columns
from indexdigest.test import Database, DatabaseTestMixin


class LimitedViewDatabase(Database, DatabaseTestMixin):
    """
    Limit test to tables from sql/0032-utf-latin-columns.sql
    """
    def get_tables(self):
        return ['0032_utf8_table', '0032_latin1_table']


class TestFullTableScan(TestCase):
    @property
    def connection(self):
        return LimitedViewDatabase.connect_dsn(DatabaseTestMixin.DSN)

    def test_latin1_columns(self):
        reports = list(check_latin_columns(self.connection))

        print(list(map(str, reports)))

        self.assertEqual(len(reports), 2)

        self.assertEqual(str(reports[0]),
                         '0032_utf8_table: "latin_column" text column has "latin1" character set defined')
        self.assertEqual(reports[0].context['column'], 'latin_column')
        self.assertEqual(reports[0].context['column_character_set'], 'latin1')
        self.assertEqual(reports[0].context['column_collation'], 'latin1_bin')

        self.assertEqual(str(reports[1]),
                         '0032_latin1_table: "name" text column has "latin1" character set defined')
        self.assertEqual(reports[1].context['column'], 'name')
        self.assertEqual(reports[1].context['column_character_set'], 'latin1')
        self.assertEqual(reports[1].context['column_collation'], 'latin1_swedish_ci')

        # assert False
