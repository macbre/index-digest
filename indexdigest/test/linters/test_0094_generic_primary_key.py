from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0094_generic_primary_key import check_generic_primary_key
from indexdigest.test import DatabaseTestMixin


class TestLinter(TestCase, DatabaseTestMixin):

    def test_generic_primary_key(self):
        reports = list(check_generic_primary_key(self.connection))

        print(list(map(str, reports)))

        assert len(reports) == 1

        assert str(reports[0]) == '0094_generic_primary_key: ' \
                                  '"0094_generic_primary_key" has a primary key called id, use a more meaningful name'
        assert reports[0].table_name == '0094_generic_primary_key'
        assert 'CREATE TABLE `0094_generic_primary_key`' in reports[0].context['schema']
