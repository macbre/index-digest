from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.not_used_indices import check_not_used_indices, \
    check_queries_not_using_indices
from indexdigest.test import DatabaseTestMixin


class TestNotUsedIndices(TestCase, DatabaseTestMixin):

    def test_not_used_indices(self):
        with open('sql/0002-not-used-indices-log') as fp:
            queries = fp.readlines()
            queries = list(map(str.strip, queries))  # remove trailing spaces

        reports = check_not_used_indices(database=self.connection, queries=queries)

        print(reports)

        self.assertEqual(len(reports), 1)
        self.assertEqual(str(reports[0]), '0002_not_used_indices: "test_id_idx" index was not used by provided queries')
        self.assertEqual(reports[0].table_name, '0002_not_used_indices')
        self.assertEqual(str(reports[0].context['not_used_index']), 'KEY test_id_idx (test, id)')

        # assert False


class TestQueriesNotUsingIndices(TestCase, DatabaseTestMixin):

    def test_queries(self):
        with open('sql/0019-queries-not-using-indices-log') as fp:
            queries = fp.readlines()
            queries = list(map(str.strip, queries))  # remove trailing spaces

        reports = check_queries_not_using_indices(database=self.connection, queries=queries)

        # print(reports)

        self.assertEqual(len(reports), 2)

        self.assertEqual(str(reports[0]), '0019_queries_not_using_indices: "SELECT id FROM 0019_queries_not_using_indices WHER..." query did not make use of any index')
        self.assertEqual(reports[0].table_name, '0019_queries_not_using_indices')
        self.assertEqual(str(reports[0].context['query']), 'SELECT id FROM 0019_queries_not_using_indices WHERE foo = "test" OR id > 1;')
        self.assertEqual(str(reports[0].context['explain_extra']), 'Using where')
        self.assertEqual(str(reports[0].context['explain_rows']), '3')

        self.assertEqual(reports[1].table_name, '0019_queries_not_using_indices')
        self.assertEqual(str(reports[1].context['query']), 'SELECT id FROM 0019_queries_not_using_indices WHERE foo = "test"')
        self.assertEqual(str(reports[1].context['explain_extra']), 'Using where')
        self.assertEqual(str(reports[1].context['explain_rows']), '3')

        # assert False
