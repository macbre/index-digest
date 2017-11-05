from __future__ import print_function

from indexdigest.linters import check_queries_using_filesort
from indexdigest.test import BigTableTest


class TestBigTableLinters(BigTableTest):

    def test_filesort(self):
        queries = [
            # Using where; Using index -- and that's good :)
            'SELECT count(*) FROM 0020_big_table WHERE id BETWEEN 10 AND 20',
            # Using where; Using filesort
            'SELECT * FROM 0020_big_table WHERE id BETWEEN 10 AND 20 ORDER BY val',
            # Using where; Using temporary; Using filesort
            'SELECT val, count(*) FROM 0020_big_table WHERE id BETWEEN 10 AND 20 GROUP BY val',
        ]

        reports = list(check_queries_using_filesort(self.connection, queries))

        # reports ordered is the same as schema columns order
        self.assertEqual(len(reports), 2)

        self.assertEqual(str(reports[0]), '0020_big_table: "SELECT * FROM 0020_big_table WHERE id BETWEEN 10 A..." query used filesort')
        self.assertEqual(reports[0].context['query'], 'SELECT * FROM 0020_big_table WHERE id BETWEEN 10 AND 20 ORDER BY val')
        self.assertEqual(reports[0].context['explain_extra'], 'Using where; Using filesort')
        self.assertEqual(reports[0].context['explain_rows'], 11)

        self.assertEqual(str(reports[1]), '0020_big_table: "SELECT val, count(*) FROM 0020_big_table WHERE id ..." query used filesort')
        self.assertEqual(reports[1].context['query'], 'SELECT val, count(*) FROM 0020_big_table WHERE id BETWEEN 10 AND 20 GROUP BY val')
        self.assertEqual(reports[1].context['explain_extra'], 'Using where; Using temporary; Using filesort')
        self.assertEqual(reports[1].context['explain_rows'], 11)

        # assert False
