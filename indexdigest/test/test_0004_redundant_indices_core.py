from __future__ import print_function

from unittest import TestCase

from indexdigest.test import DatabaseTestMixin


class RedundantIndicesTest(TestCase, DatabaseTestMixin):

    def test_redundant_index_with_primary(self):
        indices = self.connection.get_table_indices('0004_id_foo')
        print(indices)

        (idx, primary) = indices

        self.assertEqual(primary.name, 'PRIMARY')
        self.assertEqual(idx.name, 'idx')

        self.assertTrue(idx.is_covered_by(primary))
        self.assertFalse(primary.is_covered_by(idx))

    def test_redundant_indexes(self):
        indices = self.connection.get_table_indices('0004_id_foo_bar')
        print(indices)

        (idx_foo, idx_foo_bar, idx_id_foo, primary) = indices

        self.assertEqual(primary.name, 'PRIMARY')
        self.assertEqual(idx_foo.name, 'idx_foo')
        self.assertEqual(idx_foo_bar.name, 'idx_foo_bar')
        self.assertEqual(idx_id_foo.name, 'idx_id_foo')

        self.assertTrue(idx_foo.is_covered_by(idx_foo_bar))

        self.assertFalse(idx_foo.is_covered_by(idx_id_foo))
        self.assertFalse(idx_foo.is_covered_by(primary))
        self.assertFalse(primary.is_covered_by(idx_foo))
