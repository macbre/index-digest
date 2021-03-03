from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0031_low_cardinality_index import \
    check_low_cardinality_index, get_low_cardinality_indices, INDEX_CARDINALITY_THRESHOLD
from indexdigest.test import DatabaseTestMixin


class TestLinter(TestCase, DatabaseTestMixin):

    def setUp(self) -> None:
        self.skipTest(reason="test_0031_low_cardinality_index is not stable")

    def test_get_low_cardinality_indices(self):
        indices = list(get_low_cardinality_indices(self.connection))

        print(indices)

        assert len(indices) == 1

        index = indices[0]
        assert index[0] == '0020_big_table'
        assert index[2]['INDEX_NAME'] == 'num_idx'
        assert index[2]['COLUMN_NAME'] == 'num'
        assert index[2]['CARDINALITY'] >= 1
        assert index[2]['CARDINALITY'] <= INDEX_CARDINALITY_THRESHOLD

    def test_low_cardinality_index(self):
        reports = list(check_low_cardinality_index(self.connection))

        print(reports, reports[0].context)

        assert len(reports) == 1

        assert str(reports[0]) == '0020_big_table: "num_idx" index on "num" column ' \
                                  'has low cardinality, check if it is needed'
        assert reports[0].table_name == '0020_big_table'

        assert reports[0].context['column_name'] == 'num'
        assert reports[0].context['index_name'] == 'num_idx'
        assert isinstance(reports[0].context['index_cardinality'], int)

        self.assertAlmostEqual(int(reports[0].context['value_usage']), 50, delta=5)
