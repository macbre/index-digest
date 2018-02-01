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

    def test_data_not_updated_recently_with_custom_threshold(self):
        env = {
            'INDEX_DIGEST_DATA_NOT_UPDATED_RECENTLY_THRESHOLD_DAYS': str(60 * 86400)
        }

        reports = list(check_data_not_updated_recently(self.connection, env))

        print(list(map(str, reports)))
        assert len(reports) == 0
