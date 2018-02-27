from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0118_high_offset_selects import check_high_offset_selects
from indexdigest.test import DatabaseTestMixin, read_queries_from_log


class TestLinter(TestCase, DatabaseTestMixin):

    def test_high_offset_selects(self):
        reports = list(check_high_offset_selects(
            self.connection, queries=read_queries_from_log('0118-high-offset-selects-log')))

        print(reports, reports[0].context)

        self.assertEqual(len(reports), 1)

        self.assertEqual(str(reports[0]), 'page: "SELECT /* CategoryPaginationViewer::processSection..." query uses too high offset impacting the performance')
        self.assertEqual(reports[0].table_name, 'page')
        self.assertEqual(str(reports[0].context['query']), "SELECT /* CategoryPaginationViewer::processSection */  page_namespace,page_title,page_len,page_is_redirect,cl_sortkey_prefix  FROM `page` INNER JOIN `categorylinks` FORCE INDEX (cl_sortkey) ON ((cl_from = page_id))  WHERE cl_type = 'page' AND cl_to = 'Spotify/Song'  ORDER BY cl_sortkey LIMIT 927600,200")
        self.assertEqual(reports[0].context['limit'], 200)
        self.assertEqual(reports[0].context['offset'], 927600)

        # assert False
