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
        return

        reports = list(check_selects_with_like(
            database=self.connection, queries=read_queries_from_log('0027-selects-with-like-log')))

        print(reports)

        self.assertEqual(len(reports), 1)

        self.assertEqual(str(reports[0]), '0019_queries_not_using_indices: "SELECT id FROM 0019_queries_not_using_indices WHER..." query did not make use of any index')
        self.assertEqual(reports[0].table_name, '0019_queries_not_using_indices')
        self.assertEqual(str(reports[0].context['query']), 'SELECT id FROM 0019_queries_not_using_indices WHERE foo = "test" OR id > 1;')
        self.assertEqual(str(reports[0].context['explain_extra']), 'Using where')
        self.assertEqual(str(reports[0].context['explain_rows']), '3')

        self.assertEqual(reports[1].table_name, '0019_queries_not_using_indices')
        self.assertEqual(str(reports[1].context['query']), 'SELECT id FROM 0019_queries_not_using_indices WHERE foo = "test"')
        self.assertEqual(str(reports[1].context['explain_extra']), 'Using where')
        self.assertEqual(str(reports[1].context['explain_rows']), '3')

        assert False
