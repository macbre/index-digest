from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0164_empty_database import check_empty_database
from indexdigest.test import DatabaseTestMixin


class TestLinter(TestCase, DatabaseTestMixin):

    def test_empty_database(self):
        reports = list(check_empty_database(self.connection))

        print(reports, reports[0].context)

        assert len(reports) == 1

        assert str(reports[0]) == 'index_digest_empty: "index_digest_empty" database has no tables'
        assert reports[0].table_name == 'index_digest_empty'
