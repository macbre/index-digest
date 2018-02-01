from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0028_data_not_updated_recently import check_data_not_updated_recently
from indexdigest.test import DatabaseTestMixin
from .test_0028_data_too_old import LimitedViewDatabase


class TestLinter(TestCase, DatabaseTestMixin):

    @property
    def connection(self):
        return LimitedViewDatabase.connect_dsn(self.DSN)

    def test_data_not_updated_recently(self):
        reports = list(check_data_not_updated_recently(self.connection))

        print(list(map(str, reports)))

        assert len(reports) == 1

        assert str(reports[0]).startswith('0028_data_not_updated_recently: "0028_data_not_updated_recently" '
                                          'has the latest row added 4')  # 40 days ago
        assert str(reports[0]).endswith('consider checking if it should be up-to-date')
        self.assertAlmostEquals(reports[0].context['diff_days'], 40)
        assert reports[0].table_name == '0028_data_not_updated_recently'

        assert 'data_since' in reports[0].context
        assert 'data_until' in reports[0].context

    def test_data_not_updated_recently_with_custom_threshold(self):
        env = {
            'INDEX_DIGEST_DATA_NOT_UPDATED_RECENTLY_THRESHOLD_DAYS': str(60 * 86400)
        }

        reports = list(check_data_not_updated_recently(self.connection, env))

        print(list(map(str, reports)))
        assert len(reports) == 0
