# -*- coding: utf8 -*-
from __future__ import print_function

from unittest import TestCase

from indexdigest.test import DatabaseTestMixin, DatabaseWithMockedRow
from indexdigest.database import DatabaseBase


class TestDatabaseBase(TestCase, DatabaseTestMixin):

    def test_database_connect(self):
        conn = DatabaseBase(host='127.0.0.1', user='index_digest', passwd='qwerty', db='index_digest')
        self.assertIsInstance(conn, DatabaseBase)

    def test_database_connect_dsn(self):
        self.assertIsInstance(self.connection, DatabaseBase)

    def test_query_list(self):
        res = list(self.connection.query_list('SHOW DATABASES'))

        self.assertTrue('information_schema' in res, res)
        self.assertTrue('index_digest' in res, res)

    def test_query_field(self):
        cnt = self.connection.query_field('SELECT count(*) FROM 0000_the_table')

        self.assertEqual(cnt, 3)

    def test_query_row(self):
        row = self.connection.query_row('SELECT * FROM 0000_the_table WHERE id = 1')

        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], 'test')

    def test_query_dict_row(self):
        row = self.connection.query_dict_row('SELECT * FROM 0000_the_table ORDER BY 1')
        print(row)

        self.assertEqual(row['id'], 1)
        self.assertEqual(row['foo'], 'test')

    def test_query_dict_rows(self):
        rows = list(self.connection.query_dict_rows('SELECT * FROM 0000_the_table ORDER BY 1'))
        row = rows[0]
        print(row)

        self.assertEqual(len(rows), 3)

        self.assertEqual(row['id'], 1)
        self.assertEqual(row['foo'], 'test')


class TestDatabase(TestCase, DatabaseTestMixin):

    TABLE_NAME = '0000_the_table'

    def test_database_version(self):
        version = self.connection.get_server_version()  # 5.5.57-0+deb8u1 / 8.0.3-rc-log

        self.assertTrue(
            version.startswith('5.') or version.startswith('8.'),
            'MySQL server should be from 5.x or 8.x line')

    def test_get_tables(self):
        tables = list(self.connection.get_tables())
        print(tables)

        self.assertTrue(self.TABLE_NAME in tables)

    def test_get_variables(self):
        variables = self.connection.get_variables()
        print(variables)

        self.assertTrue('version_compile_os' in variables)
        self.assertTrue('innodb_version' in variables)

    def test_get_variables_like(self):
        variables = self.connection.get_variables(like='innodb')
        print(variables)

        self.assertFalse('version_compile_os' in variables)  # this variable does not match given like
        self.assertTrue('innodb_version' in variables)

    def test_explain_and_utf_query(self):
        """
        mysql> explain SELECT * FROM 0000_the_table WHERE foo = "foo ąęź";
        +----+-------------+----------------+------+---------------+---------+---------+-------+------+--------------------------+
        | id | select_type | table          | type | possible_keys | key     | key_len | ref   | rows | Extra                    |
        +----+-------------+----------------+------+---------------+---------+---------+-------+------+--------------------------+
        |  1 | SIMPLE      | 0000_the_table | ref  | idx_foo       | idx_foo | 50      | const |    1 | Using where; Using index |
        +----+-------------+----------------+------+---------------+---------+---------+-------+------+--------------------------+
        1 row in set (0.00 sec)
        """
        res = list(self.connection.explain_query('SELECT * FROM {} WHERE foo = "foo ąęź"'.format(self.TABLE_NAME)))
        row = res[0]
        print(row)

        self.assertEqual(len(res), 1)
        self.assertEqual(row['key'], 'idx_foo')
        self.assertEqual(row['table'], self.TABLE_NAME)
        self.assertTrue('Using index' in row['Extra'])

    def test_get_table_indices(self):
        """
        mysql> SELECT INDEX_NAME, NON_UNIQUE, SEQ_IN_INDEX, COLUMN_NAME, CARDINALITY
        FROM INFORMATION_SCHEMA.STATISTICS WHERE table_name = '0000_the_table'
        ORDER BY INDEX_NAME, SEQ_IN_INDEX;
        +------------+------------+--------------+-------------+-------------+
        | INDEX_NAME | NON_UNIQUE | SEQ_IN_INDEX | COLUMN_NAME | CARDINALITY |
        +------------+------------+--------------+-------------+-------------+
        | idx_foo    | 1          |            1 | foo         |           3 |
        | PRIMARY    | 0          |            1 | id          |           3 |
        | PRIMARY    | 0          |            2 | foo         |           3 |
        +------------+------------+--------------+-------------+-------------+
        3 rows in set (0.00 sec)
        """
        (idx, primary) = self.connection.get_table_indices(self.TABLE_NAME)
        print(idx, primary)

        self.assertEqual(idx.name, 'idx_foo')
        self.assertEqual(primary.name, 'PRIMARY')

        self.assertListEqual(idx.columns, ['foo'])
        self.assertListEqual(primary.columns, ['id', 'foo'])

        self.assertFalse(idx.is_primary)
        self.assertFalse(idx.is_unique)
        self.assertTrue(primary.is_primary, 'Primary key is correctly detected')
        self.assertTrue(primary.is_unique, 'Primary key should be treated as a unique one')

        # assert False

    def test_get_table_schema(self):
        schema = self.connection.get_table_schema(self.TABLE_NAME)
        print(schema)

        self.assertTrue('CREATE TABLE `0000_the_table` (' in schema)
        self.assertTrue('PRIMARY KEY (`id`,`foo`),' in schema)
        self.assertTrue('ENGINE=InnoDB' in schema)

        # assert False

    def test_get_table_metadata(self):
        meta = self.connection.get_table_metadata(self.TABLE_NAME)
        print(meta)

        # stats
        self.assertEqual(meta['engine'], 'InnoDB')
        self.assertEqual(meta['rows'], 3)
        self.assertTrue(meta['index_size'] > 0)
        self.assertTrue(meta['data_size'] > 0)

        # assert False

    def test_get_table_columns(self):
        columns = self.connection.get_table_columns(self.TABLE_NAME)
        print(columns)

        # the columns order is maintained
        column_names = [column.name for column in columns]

        # columns
        self.assertTrue('id' in column_names)
        self.assertTrue('foo' in column_names)

        self.assertEqual(columns[0].name, 'id')
        self.assertEqual(columns[0].type, 'int(9)')
        self.assertIsNone(columns[0].character_set)  # numeric column

        self.assertEqual(columns[1].name, 'foo')
        self.assertEqual(columns[1].type, 'varchar(16)')
        self.assertEqual(columns[1].character_set, 'utf8')

        self.assertEqual(len(columns), 2)

        # assert False


class TestsWithDatabaseMocked(TestCase):

    def test_database_hostname(self):
        db = DatabaseWithMockedRow(mocked_row=['hostname', 'kopytko.foo.net'])
        self.assertEquals(db.get_server_hostname(), 'kopytko.foo.net')

    def test_database_version(self):
        db = DatabaseWithMockedRow(mocked_row=['5.5.58-0+deb8u1'])
        self.assertEquals(db.get_server_version(), '5.5.58-0+deb8u1')


class TestMemoization(TestCase):

    def test_get_queries(self):
        db = DatabaseWithMockedRow(mocked_row=['foo'])

        # query method is not memoized, so let's count all queries (even the same ones)
        for _ in range(5):
            self.assertEquals(db.query_row('SELECT FOO'), ['foo'])

        self.assertEquals(len(db.get_queries()), 5)
        self.assertEquals(db.get_queries()[0], 'SELECT FOO')

    def test_cached_get_tables(self):
        tables_list = ['foo']
        db = DatabaseWithMockedRow(mocked_row=tables_list)

        # this would made five queries to database if not memoization in get_tables
        for _ in range(5):
            self.assertEquals(db.get_tables(), tables_list)

        # however, only one is made :)
        self.assertEquals(len(db.get_queries()), 1)
