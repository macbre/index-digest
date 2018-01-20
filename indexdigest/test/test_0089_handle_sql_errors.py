from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0006_not_used_columns_and_tables import get_used_tables_from_queries
from indexdigest.utils import explain_queries

from indexdigest.test import DatabaseTestMixin, read_queries_from_log


class ErrorsHandlingTest(TestCase, DatabaseTestMixin):

    @property
    def queries(self):
        return read_queries_from_log('0098-handle-sql-errors-log')

    def test_get_used_tables_from_queries(self):
        tables = get_used_tables_from_queries(self.queries)

        print(tables)

        assert '0020_big_table' in tables
        # assert False

    def test_explain_queries(self):
        res = list(explain_queries(self.connection, self.queries))
        tables_used = [item[1] for item in res]

        print(res, tables_used)

        assert '0020_big_table' in tables_used
        # assert False

    def test_get_table_columns(self):
        res = self.connection.get_table_columns('t')
        self.assertIsNone(res)

        # assert False
