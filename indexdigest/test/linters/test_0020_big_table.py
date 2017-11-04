from __future__ import print_function

from indexdigest.test import BigTableTest


class TestBigTableLinters(BigTableTest):

    def test_filesort(self):
        queries = [
            # Using where; Using filesort
            'SELECT * FROM 0020_big_table WHERE id BETWEEN 10 AND 20 ORDER BY val',
            # Using where; Using temporary; Using filesort
            'SELECT val, count(*) FROM 0020_big_table WHERE id BETWEEN 10 AND 20 GROUP BY val',
        ]

        for query in queries:
            print(query, list(self.connection.explain_query(query)))

        # assert False
