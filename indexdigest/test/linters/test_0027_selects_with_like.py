from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0027_selects_with_like import check_selects_with_like, query_uses_leftmost_like
from indexdigest.test import DatabaseTestMixin, read_queries_from_log


class TestSelectsWithLike(TestCase, DatabaseTestMixin):

    def test_query_uses_leftmost_like(self):
        self.assertTrue(query_uses_leftmost_like("SELECT * FROM foo WHERE bar LIKE '%baz';"))
        self.assertTrue(query_uses_leftmost_like('SELECT * FROM foo WHERE bar LIKE "%baz";'))
        self.assertTrue(query_uses_leftmost_like('SELECT * FROM foo WHERE bar like "%baz";'))
        self.assertTrue(query_uses_leftmost_like('SELECT * FROM foo WHERE bar like "%123";'))
        self.assertTrue(query_uses_leftmost_like('SELECT * FROM foo WHERE bar like\n"%123";'))
        self.assertTrue(query_uses_leftmost_like('SELECT * FROM foo WHERE bar like  "%123";'))

        self.assertFalse(query_uses_leftmost_like("SELECT * FROM foo WHERE bar = 'baz'"))
        self.assertFalse(query_uses_leftmost_like("SELECT * FROM foo WHERE like = 'foo'"))
        self.assertFalse(query_uses_leftmost_like("SELECT * FROM foo WHERE bar LIKE 'b%z';"))
        self.assertFalse(query_uses_leftmost_like("SELECT * FROM foo WHERE bar LIKE 'ba%';"))

    def test_queries(self):
        reports = list(check_selects_with_like(
            database=self.connection, queries=read_queries_from_log('0027-selects-with-like-log')))

        print(reports, reports[0].context)

        self.assertEqual(len(reports), 1)

        self.assertEqual(str(reports[0]), '0020_big_table: "SELECT * FROM 0020_big_table WHERE text LIKE \'%00\'" query uses LIKE with left-most wildcard')
        self.assertEqual(reports[0].table_name, '0020_big_table')
        self.assertEqual(str(reports[0].context['query']), 'SELECT * FROM 0020_big_table WHERE text LIKE \'%00\'')
        self.assertEqual(str(reports[0].context['explain_extra']), 'Using where')
        self.assertTrue(reports[0].context['explain_rows'] > 10000)

        # assert False
