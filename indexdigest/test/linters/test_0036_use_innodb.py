from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0036_use_innodb import check_use_innodb
from indexdigest.test import DatabaseTestMixin


class TestLinter(TestCase, DatabaseTestMixin):

    def test_use_innodb(self):
        reports = list(check_use_innodb(self.connection))

        print(reports, reports[0].context)

        self.assertEqual(len(reports), 1)

        self.assertEqual(str(reports[0]),
                         '0036_use_innodb_myisam: "0036_use_innodb_myisam" uses MyISAM storage engine')
        self.assertEqual(reports[0].table_name, '0036_use_innodb_myisam')
        self.assertEqual(str(reports[0].context['engine']), "MyISAM")

        # assert False
