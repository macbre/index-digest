from __future__ import print_function

from unittest import TestCase

from indexdigest.linters import check_test_tables
from indexdigest.linters.linter_0075_test_tables import is_test_table
from indexdigest.test import DatabaseTestMixin


class TestTables(TestCase, DatabaseTestMixin):

    def test_is_test_table(self):
        assert is_test_table('test') is True
        assert is_test_table('some_guy_test_table') is True
        assert is_test_table('0075_some_guy_test_table') is True
        assert is_test_table('foo_test_bar') is True
        assert is_test_table('test_bar') is True
        assert is_test_table('foo_test') is True
        assert is_test_table('forum_creation_temp') is True

        assert is_test_table('foo_testing') is False
        assert is_test_table('test123') is False
        assert is_test_table('travis_tests') is False

    def test_check_test_table(self):
        reports = list(check_test_tables(self.connection))

        print(list(map(str, reports)))

        self.assertEqual(len(reports), 2)

        self.assertEqual(str(reports[0]),
                         '0004_image_comment_temp: "0004_image_comment_temp" seems to be a test table')
        self.assertTrue('CREATE TABLE `0004_image_comment_temp` (' in reports[0].context['schema'])

        self.assertEqual(str(reports[1]),
                         '0075_some_guy_test_table: "0075_some_guy_test_table" seems to be a test table')
        self.assertTrue('CREATE TABLE `0075_some_guy_test_table` (' in reports[1].context['schema'])

        # assert False
