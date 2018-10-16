from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0031_low_cardinality_index import \
    check_low_cardinality_index, get_low_cardinality_indices
from indexdigest.test import DatabaseTestMixin


class TestLinter(TestCase, DatabaseTestMixin):

    def test_get_low_cardinality_indices(self):
        indices = list(get_low_cardinality_indices(self.connection))

        print(indices)

        assert len(indices) == 1
        assert indices[0][0] == '0020_big_table'
        assert indices[0][2]['INDEX_NAME'] == 'num_idx'
        assert indices[0][2]['COLUMN_NAME'] == 'num'
        assert indices[0][2]['CARDINALITY'] == 2

    def test_low_cardinality_index(self):
        reports = list(check_low_cardinality_index(self.connection))

        print(reports, reports[0].context)

        assert len(reports) == 1

        assert str(reports[0]) == '0020_big_table: "num_idx" index on "num" column ' \
                                  'has low cardinality, check if it is needed'
        assert reports[0].table_name == '0020_big_table'
        assert int(reports[0].context['value_usage']) == 33
