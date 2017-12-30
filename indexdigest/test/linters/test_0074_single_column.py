from __future__ import print_function

from unittest import TestCase

from indexdigest.linters import check_single_column
from indexdigest.test import DatabaseTestMixin


class TestSingleColumn(TestCase, DatabaseTestMixin):

    def test_check_single_column(self):
        reports = list(check_single_column(self.connection))

        print(list(map(str, reports)))

        self.assertEqual(len(reports), 1)

        self.assertEqual(str(reports[0]),
                         '0074_bag_of_ints: "0074_bag_of_ints" has just a single column')
        self.assertTrue('CREATE TABLE `0074_bag_of_ints` (' in reports[0].context['schema'])

        # assert False
