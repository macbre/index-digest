from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0070_insert_ignore import \
    remove_comments, is_insert_ignore_query, check_insert_ignore_queries
from indexdigest.test import DatabaseTestMixin, read_queries_from_log


class TestInsertIgnore(TestCase, DatabaseTestMixin):

    def test_remove_comments(self):
        self.assertEqual(
            'INSERT  IGNORE',
            remove_comments('INSERT /* foo */ IGNORE')
        )

        self.assertEqual(
            'SELECT foo',
            remove_comments('/* foo */SELECT/* test*/ foo')
        )

    def test_is_insert_ignore_query(self):
        assert is_insert_ignore_query("INSERT IGNORE INTO 0070_insert_ignore VALUES ('2017-01-01', 9, 123);") is True
        assert is_insert_ignore_query("INSERT IGN/*bar*/ORE INTO 0070_insert_ignore VALUES ('2017-01-01', 9, 123);") is True
        assert is_insert_ignore_query("Insert /* foo */ Ignore INTO 0070_insert_ignore VALUES ('2017-01-01', 9, 123);") is True
        assert is_insert_ignore_query("/* foo */ INSERT IGNORE INTO `0070_insert_ignore` VALUES (9, '123', '2017-01-01');") is True

        assert is_insert_ignore_query("/* INSERT IGNORE */ INSERT INTO 0070_insert_ignore VALUES ('2017-01-01', 9, 123);") is False
        assert is_insert_ignore_query("INSERT INTO 0070_insert_ignore VALUES ('INSERT IGNORE', 9, 123);") is False

    def test_queries(self):
        reports = list(check_insert_ignore_queries(
            database=self.connection, queries=read_queries_from_log('0070-insert-ignore-log')))

        print(reports)

        self.assertEqual(len(reports), 4)

        self.assertEqual(str(reports[0]), '0070_insert_ignore: "INSERT IGNORE INTO `0070_insert_ignore` VALUES (9,..." query uses a risky INSERT IGNORE')
        self.assertEqual(reports[0].table_name, '0070_insert_ignore')
        self.assertEqual(str(reports[0].context['query']), "INSERT IGNORE INTO `0070_insert_ignore` VALUES (9, '123', '2017-01-01');")
        assert 'CREATE TABLE `0070_insert_ignore` (' in str(reports[0].context['schema'])

        self.assertEqual(str(reports[1].context['query']), "/* foo */ INSERT IGNORE INTO `0070_insert_ignore` VALUES (9, '123', '2017-01-01');")
        self.assertEqual(str(reports[2].context['query']), "INSERT  IGNORE INTO `0070_insert_ignore` VALUES ('123', 9, '2017-01-01');")
        self.assertEqual(str(reports[3].context['query']), "INSERT /* foo */ IGNORE INTO `0070_insert_ignore` VALUES ('2017-01-01', 9, 123);")
        # assert False
