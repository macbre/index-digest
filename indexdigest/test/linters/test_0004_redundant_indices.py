from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0004_redundant_indices import get_redundant_indices, check_redundant_indices
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
            lambda i: i.table_name.startswith('0004_'),
            reports
        ))

        print(list(map(str,reports)))

        self.assertEqual(len(reports), 3)
        self.assertEqual(str(reports[0]), '0004_id_foo: "idx" index can be removed as redundant (covered by "PRIMARY")')
        self.assertEqual(str(reports[1]), '0004_id_foo_bar: "idx_foo" index can be removed as redundant (covered by "idx_foo_bar")')
        self.assertEqual(str(reports[2]), '0004_indices_duplicating_each_other: "idx_foo" index can be removed as redundant (covered by "idx_foo_2")')

        report = reports[0]

        print(report, report.context)

        self.assertEqual(str(report.context['redundant']), 'UNIQUE KEY idx (item_id, foo)')
        self.assertEqual(str(report.context['covered_by']), 'PRIMARY KEY (item_id, foo)')

        # and we have size reported as well (see #16)
        self.assertTrue(report.context['table_data_size_mb'] > 0)
        self.assertTrue(report.context['table_index_size_mb'] > 0)

        # and we a schema reported in the context (see #16)
        self.assertTrue('CREATE TABLE' in report.context['schema'])
        self.assertTrue('AUTO_INCREMENT' in report.context['schema'])
        self.assertTrue('ENGINE=' in report.context['schema'])

        # assert False
