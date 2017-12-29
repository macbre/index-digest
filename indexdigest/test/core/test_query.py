from unittest import TestCase

from indexdigest.query import get_query_columns, get_query_tables


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

    def test_get_query_tables(self):
        self.assertListEqual(['test_table'],
                             get_query_tables('SELECT * FROM `test_table`'))

        self.assertListEqual(['0001_test_table'],
                             get_query_tables('SELECT * FROM `0001_test_table`'))

        self.assertListEqual(['test_table'],
                             get_query_tables('SELECT foo FROM `test_table`'))

        self.assertListEqual(['test_table'],
                             get_query_tables('SELECT foo FROM test_table WHERE id = 1'))

        self.assertListEqual(['test_table', 'second_table'],
                             get_query_tables('SELECT foo FROM test_table, second_table WHERE id = 1'))

        self.assertListEqual(['revision', 'page', 'wikicities_user'],
                             get_query_tables('SELECT rev_id,rev_page,rev_text_id,rev_timestamp,rev_comment,rev_user_text,rev_user,rev_minor_edit,rev_deleted,rev_len,rev_parent_id,rev_shaN,page_namespace,page_title,page_id,page_latest,user_name FROM `revision` INNER JOIN `page` ON ((page_id = rev_page)) LEFT JOIN `wikicities_user` ON ((rev_user != N) AND (user_id = rev_user)) WHERE rev_id = X LIMIT N'))

        self.assertListEqual(['events'],
                             get_query_tables("SELECT COUNT( 0 ) AS cnt, date_format(event_date, '%Y-%m-%d') AS date 	 FROM events 	 WHERE event_date BETWEEN '2017-10-18 00:00:00' 	 AND '2017-10-24 23:59:59'  	 AND wiki_id = '1289985' GROUP BY date WITH ROLLUP"))

        # INSERT queries
        self.assertListEqual(['0070_insert_ignore_table'],
                             get_query_tables("INSERT IGNORE INTO `0070_insert_ignore_table` VALUES (9, '123', '2017-01-01');"))

        self.assertListEqual(['0070_insert_ignore_table'],
                             get_query_tables("INSERT into `0070_insert_ignore_table` VALUES (9, '123', '2017-01-01');"))

        # assert False
