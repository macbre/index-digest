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
            lambda i: i.table_name.startswith('0004_'),
            reports
        ))

        print(reports)

        self.assertEqual(len(reports), 2)
        self.assertEqual(str(reports[0]), '0004_id_foo: UNIQUE KEY idx (id, foo) index can be removed as redundant (covered by PRIMARY KEY (id, foo))')
        self.assertEqual(str(reports[1]), '0004_id_foo_bar: KEY idx_foo (foo) index can be removed as redundant (covered by KEY idx_foo_bar (foo, bar))')

        report = reports[0]

        print(report, report.context)

        self.assertEquals(str(report.context['redundant']), 'UNIQUE KEY idx (id, foo)')
        self.assertEquals(str(report.context['covered_by']), 'PRIMARY KEY (id, foo)')

        # and we have size reported as well (see #16)
        self.assertTrue(report.context['table_data_size_mb'] > 0)
        self.assertTrue(report.context['table_index_size_mb'] > 0)

        # and we a schema reported in the context (see #16)
        self.assertTrue('CREATE TABLE' in report.context['schema'])
        self.assertTrue('AUTO_INCREMENT' in report.context['schema'])
        self.assertTrue('ENGINE=' in report.context['schema'])

        # assert False
