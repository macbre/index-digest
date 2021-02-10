from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0019_queries_not_using_indices import check_queries_not_using_indices
from indexdigest.test import DatabaseTestMixin, read_queries_from_log


class TestQueriesNotUsingIndices(TestCase, DatabaseTestMixin):

    def test_queries(self):
        reports = list(check_queries_not_using_indices(
            database=self.connection, queries=read_queries_from_log('0019-queries-not-using-indices-log')))

        print(*[f"{report.message} ({report.context['explain_extra']})" for report in reports], sep="\n")
        assert len(reports) == 3

        self.assertEqual(str(reports[0]), '0019_queries_not_using_indices: "SELECT item_id FROM 0019_queries_not_using_indices..." query did not make use of any index')
        self.assertEqual(reports[0].table_name, '0019_queries_not_using_indices')
        self.assertEqual(str(reports[0].context['query']), 'SELECT item_id FROM 0019_queries_not_using_indices WHERE foo = "test" OR item_id > 1;')
        self.assertEqual(str(reports[0].context['explain_extra']), 'Using where')
        self.assertEqual(str(reports[0].context['explain_rows']), '3')

        self.assertEqual(reports[1].table_name, '0019_queries_not_using_indices')
        self.assertEqual(str(reports[1].context['query']), 'SELECT item_id FROM 0019_queries_not_using_indices WHERE foo = "test"')
        self.assertEqual(str(reports[1].context['explain_extra']), 'Using where')
        self.assertEqual(str(reports[1].context['explain_rows']), '3')

        self.assertEqual(reports[2].table_name, '0019_queries_not_using_indices')
        self.assertEqual(str(reports[2].context['query']), 'SELECT 1 AS one FROM dual WHERE exists ( SELECT item_id FROM 0019_queries_not_using_indices WHERE foo = "test" );')
        self.assertEqual(str(reports[2].context['explain_extra']), 'Using where')
        self.assertEqual(str(reports[2].context['explain_rows']), '3')

        # assert False
