from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0002_not_used_indices import check_not_used_indices
from indexdigest.test import DatabaseTestMixin, read_queries_from_log


class TestNotUsedIndices(TestCase, DatabaseTestMixin):

    def test_not_used_indices(self):
        reports = list(check_not_used_indices(
            database=self.connection, queries=read_queries_from_log('0002-not-used-indices-log')))

        print(reports)

        self.assertEqual(len(reports), 1)
        self.assertEqual(str(reports[0]), '0002_not_used_indices: "test_id_idx" index was not used by provided queries')
        self.assertEqual(reports[0].table_name, '0002_not_used_indices')
        self.assertEqual(str(reports[0].context['not_used_index']), 'KEY test_id_idx (test, item_id)')

        # assert False
