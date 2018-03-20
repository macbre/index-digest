from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0032_utf_latin_columns import \
    check_latin_columns, is_text_column_latin
from indexdigest.schema import Column
from indexdigest.test import Database, DatabaseTestMixin


class TestIsTextColumnLatin(TestCase):

    def test_is_text_column_non_latin(self):
        for character_set in ['utf8', 'ucs2', 'utf8mb4', 'utf16', 'utf16le', 'utf32', 'binary']:
            column = Column(name='foo', column_type='varchar', character_set=character_set)

            assert is_text_column_latin(column) is False, character_set

    def test_is_text_column_latin(self):
        # @see https://dev.mysql.com/doc/refman/5.7/en/charset-mysql.html
        for character_set in ['big5', 'latin1', 'latin2']:
            column = Column(name='foo', column_type='varchar', character_set=character_set)

            assert is_text_column_latin(column) is True, character_set

    def test_blob_column(self):
        assert is_text_column_latin(Column(name='foo', column_type='blob')) is False


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

        self.assertEqual(len(reports), 3)

        self.assertEqual(str(reports[0]),
                         '0032_utf8_table: "latin_column" text column has "latin1" character set defined')
        self.assertEqual(reports[0].context['column'], 'latin_column')
        self.assertEqual(reports[0].context['column_character_set'], 'latin1')
        self.assertEqual(reports[0].context['column_collation'], 'latin1_bin')
        assert 'CREATE TABLE `0032_utf8_table` (' in reports[0].context['schema']

        self.assertEqual(str(reports[1]),
                         '0032_utf8_table: "big5_column" text column has "big5" character set defined')
        self.assertEqual(reports[1].context['column'], 'big5_column')
        self.assertEqual(reports[1].context['column_character_set'], 'big5')
        self.assertEqual(reports[1].context['column_collation'], 'big5_chinese_ci')

        self.assertEqual(str(reports[2]),
                         '0032_latin1_table: "name" text column has "latin1" character set defined')
        self.assertEqual(reports[2].context['column'], 'name')
        self.assertEqual(reports[2].context['column_character_set'], 'latin1')
        self.assertEqual(reports[2].context['column_collation'], 'latin1_swedish_ci')

        # assert False
