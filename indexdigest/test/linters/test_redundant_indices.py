from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.redundant_indices import get_redundant_indices, check_redundant_indices
from indexdigest.test import DatabaseTestMixin


class TestRedundantIndices(TestCase, DatabaseTestMixin):

    def test_get_redundant_indices_from_database(self):
        indices = self.connection.get_table_indices('0004_id_foo_bar')
        redundant_indices = get_redundant_indices(indices)
        (entry,) = redundant_indices

        print(entry)

        self.assertEqual(len(redundant_indices), 1)

        # idx_foo is covered by idx_foo_bar
        self.assertEqual(entry[0].name, 'idx_foo')
        self.assertEqual(entry[1].name, 'idx_foo_bar')

        # assert False

    def test_check_redundant_indices(self):
        reports = check_redundant_indices(self.connection)
        reports = list(filter(
            lambda i: str(i).startswith('0004_'),
            reports
        ))

        print(reports)

        self.assertEqual(len(reports), 2)
        self.assertEqual(reports[0], '0004_id_foo: <Index> UNIQUE KEY idx (id, foo) index can be removed as redundant (covered by <Index> PRIMARY KEY (id, foo))')
        self.assertEqual(reports[1], '0004_id_foo_bar: <Index> KEY idx_foo (foo) index can be removed as redundant (covered by <Index> KEY idx_foo_bar (foo, bar))')

        # assert False
