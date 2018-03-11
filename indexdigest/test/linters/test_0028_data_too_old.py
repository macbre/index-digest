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
        return [
            '0028_data_too_old',
            '0028_data_ok',
            '0028_data_empty',
            '0028_no_time',
            '0028_data_not_updated_recently',
            '0028_revision',
        ]


class TestLinter(TestCase, DatabaseTestMixin):

    @property
    def connection(self):
        return LimitedViewDatabase.connect_dsn(self.DSN)

    def test_data_too_old(self):
        reports = list(check_data_too_old(self.connection))

        print(list(map(str, reports)))

        assert len(reports) == 1

        assert str(reports[0]).startswith('0028_data_too_old: "0028_data_too_old" has rows added 18')  # .. 184 days ago
        assert str(reports[0]).endswith('consider changing retention policy')
        # self.assertAlmostEquals(reports[0].context['diff_days'], 184)
        assert reports[0].table_name == '0028_data_too_old'

        assert 'data_since' in reports[0].context
        assert 'data_until' in reports[0].context
        assert 'table_size_mb' in reports[0].context

        assert reports[0].context['date_column_name'] == 'timestamp'

    def test_data_too_old_with_custom_threshold(self):
        env = {
            'INDEX_DIGEST_DATA_TOO_OLD_THRESHOLD_DAYS': str(365 * 86400)
        }

        reports = list(check_data_too_old(self.connection, env))

        print(list(map(str, reports)))
        assert len(reports) == 0
