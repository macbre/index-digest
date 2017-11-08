from __future__ import print_function

from indexdigest.linters import check_full_table_scan
from indexdigest.test import BigTableTest, read_queries_from_log


class TestFullTableScan(BigTableTest):

    def test_full_table_scan(self):
        reports = list(check_full_table_scan(self.connection, read_queries_from_log('0026-full-table-scan-log')))

        self.assertEqual(len(reports), 2)

        self.assertEqual(str(reports[0]),
                         '0020_big_table: "SELECT * FROM 0020_big_table" query triggered full table scan')
        self.assertEqual(reports[0].context['query'],
                         'SELECT * FROM 0020_big_table')
        self.assertTrue(reports[0].context['explain_rows'] > 8000)

        self.assertEqual(str(reports[1]),
                         '0020_big_table: "SELECT * FROM 0020_big_table LIMIT 5" query triggered full table scan')
        self.assertEqual(reports[1].context['query'],
                         'SELECT * FROM 0020_big_table LIMIT 5')
        self.assertTrue(reports[1].context['explain_rows'] > 8000)

        # assert False
