from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0006_not_used_columns_and_tables import get_used_tables_from_queries
from indexdigest.test import DatabaseTestMixin, read_queries_from_log


class ErrorsHandlingTest(TestCase, DatabaseTestMixin):

    @property
    def queries(self):
        return read_queries_from_log('0098-handle-sql-errors-log')

    def test_get_used_tables_from_queries(self):
        tables = get_used_tables_from_queries(
            database=self.connection,
            queries=self.queries)

        self.assertListEqual(['t'], tables)
        # assert False
