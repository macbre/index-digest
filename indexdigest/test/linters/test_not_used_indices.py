from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.not_used_indices import check_not_used_indices
from indexdigest.test import DatabaseTestMixin


class TestNotUsedTables(TestCase, DatabaseTestMixin):

    def test_not_used_indices(self):
        with open('sql/0002-not-used-indices-log') as fp:
            queries = fp.readlines()

        reports = check_not_used_indices(database=self.connection, queries=queries)

        print(reports)

        self.assertEqual(len(reports), 1)
        self.assertEqual(str(reports[0]), '0002_not_used_indices: "KEY test_id_idx (test, id)" was not used by provided queries')
        self.assertEqual(reports[0].table_name, '0002_not_used_indices')
        self.assertEqual(str(reports[0].context['not_used_index']), 'KEY test_id_idx (test, id)')

        # assert False
