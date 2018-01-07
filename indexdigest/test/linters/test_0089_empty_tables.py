from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0089_empty_tables import check_empty_tables
from indexdigest.test import DatabaseTestMixin


class TestLinter(TestCase, DatabaseTestMixin):

    def test_empty_tables(self):
        reports = check_empty_tables(self.connection)

        # only include tables from our test case
        reports = [
            report for report in reports
            if report.table_name.startswith('0089_')
        ]

        print(list(map(str, reports)))

        self.assertEqual(len(reports), 1)

        self.assertEqual(str(reports[0]),
                         '0089_empty_table: "0089_empty_table" table has no rows, is it really needed?')
        self.assertTrue('CREATE TABLE `0089_empty_table` (' in reports[0].context['schema'])
