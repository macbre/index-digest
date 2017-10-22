from unittest import TestCase

from indexdigest.query import get_query_columns


class TestUtils(TestCase):

    def test_get_query_columns(self):
        self.assertListEqual(['*'],
                             get_query_columns('SELECT * FROM `test_table`'))

        self.assertListEqual(['foo'],
                             get_query_columns('SELECT foo FROM `test_table`'))

        self.assertListEqual(['id', 'foo'],
                             get_query_columns('SELECT id, foo FROM test_table WHERE id = 3'))

        self.assertListEqual(['foo', 'count', 'id'],
                             get_query_columns('SELECT foo, count(*) as bar FROM `test_table` WHERE id = 3'))

        self.assertListEqual(['foo', 'test'],
                             get_query_columns('SELECT foo, test as bar FROM `test_table`'))

        self.assertListEqual(['bar'],
                             get_query_columns('SELECT /* a comment */ bar FROM test_table'))

        # assert False
