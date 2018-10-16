from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0031_low_cardinality_index import check_low_cardinality_index
from indexdigest.test import DatabaseTestMixin


class TestLinter(TestCase, DatabaseTestMixin):

    def test_low_cardinality_index(self):
        check_low_cardinality_index(self.connection)
