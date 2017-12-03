from __future__ import print_function

from unittest import TestCase

from indexdigest.linters import check_missing_primary_index
from indexdigest.test import Database, DatabaseTestMixin


class LimitedViewDatabase(Database, DatabaseTestMixin):
    """
    Limit test to tables from sql/0034-missing-primary-index
    """
    def get_tables(self):
        return ['0034_with_primary_key', '0034_with_unique_key', '0034_querycache']


class TestMissingPrimaryIndex(TestCase):
    @property
    def connection(self):
        return LimitedViewDatabase.connect_dsn(DatabaseTestMixin.DSN)

    def test_missing_primary_index(self):
        reports = list(check_missing_primary_index(self.connection))

        print(list(map(str, reports)))

        self.assertEqual(len(reports), 1)

        self.assertEqual(str(reports[0]),
                         '0034_querycache: "0034_querycache" table does not have any primary or unique index')
        self.assertTrue('CREATE TABLE `0034_querycache` (' in reports[0].context['schema'])

        # assert False
