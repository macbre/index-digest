from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.redundant_indices import get_redundant_indices
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
