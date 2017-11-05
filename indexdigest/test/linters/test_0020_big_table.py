from __future__ import print_function

from indexdigest.linters import check_queries_using_filesort, check_queries_using_temporary
from indexdigest.test import BigTableTest, read_queries_from_log


class TestBigTableLinters(BigTableTest):

    def test_filesort(self):
        reports = list(check_queries_using_filesort(self.connection, read_queries_from_log('0020-big-table-log')))

        self.assertEqual(len(reports), 2)

        self.assertEqual(str(reports[0]),
                         '0020_big_table: "SELECT * FROM 0020_big_table WHERE id BETWEEN 10 A..." query used filesort')
        self.assertEqual(reports[0].context['query'],
                         'SELECT * FROM 0020_big_table WHERE id BETWEEN 10 AND 20 ORDER BY val')
        self.assertEqual(reports[0].context['explain_extra'], 'Using where; Using filesort')
        self.assertEqual(reports[0].context['explain_rows'], 11)
        self.assertEqual(reports[0].context['explain_key'], 'PRIMARY')

        self.assertEqual(str(reports[1]),
                         '0020_big_table: "SELECT val, count(*) FROM 0020_big_table WHERE id ..." query used filesort')
        self.assertEqual(reports[1].context['query'],
                         'SELECT val, count(*) FROM 0020_big_table WHERE id BETWEEN 10 AND 20 GROUP BY val')
        self.assertEqual(reports[1].context['explain_extra'], 'Using where; Using temporary; Using filesort')
        self.assertEqual(reports[1].context['explain_rows'], 11)
        self.assertEqual(reports[1].context['explain_key'], 'PRIMARY')

        # assert False

    def test_temporary(self):
        reports = list(check_queries_using_temporary(self.connection, read_queries_from_log('0020-big-table-log')))

        self.assertEqual(len(reports), 1)

        self.assertEqual(str(reports[0]),
                         '0020_big_table: "SELECT val, count(*) FROM 0020_big_table WHERE id ..." query used temporary')
        self.assertEqual(reports[0].context['query'],
                         'SELECT val, count(*) FROM 0020_big_table WHERE id BETWEEN 10 AND 20 GROUP BY val')
        self.assertEqual(reports[0].context['explain_extra'], 'Using where; Using temporary; Using filesort')
        self.assertEqual(reports[0].context['explain_rows'], 11)
        self.assertEqual(reports[0].context['explain_key'], 'PRIMARY')

        # assert False
