from __future__ import print_function

from unittest import TestCase

from indexdigest.database import Database
from indexdigest.linters.linter_0028_data_too_old import check_data_too_old
from indexdigest.test import DatabaseTestMixin


class LimitedViewDatabase(Database, DatabaseTestMixin):
    """
    Limit test to tables
    """
    def get_tables(self):
        return ['0028_data_too_old', '0028_data_ok', '0028_data_empty']


class TestLinter(TestCase, DatabaseTestMixin):

    @property
    def connection(self):
        return LimitedViewDatabase.connect_dsn(self.DSN)

    def test_data_too_old(self):
        reports = list(check_data_too_old(self.connection))

        print(list(map(str, reports)))

        assert len(reports) == 1

        assert str(reports[0]).startswith('0028_data_too_old: "0028_data_too_old" has rows added 18')  # .. 184 days ago
        self.assertAlmostEquals(reports[0].context['diff_days'], 184)
        assert reports[0].table_name == '0028_data_too_old'

        assert 'data_since' in reports[0].context
        assert 'data_until' in reports[0].context
