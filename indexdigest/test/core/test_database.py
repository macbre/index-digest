from __future__ import print_function

from unittest import TestCase

from indexdigest.database import DatabaseBase, Database


class DatabaseTestMixin(object):
    DSN = 'mysql://index_digest:qwerty@localhost/index_digest'

    @property
    def connection(self):
        return Database.connect_dsn(self.DSN)


class TestDatabaseBase(TestCase, DatabaseTestMixin):

    def test_database_connect(self):
        conn = DatabaseBase(host='localhost', user='index_digest', passwd='qwerty', db='index_digest')
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

    def test_database_version(self):
        version = self.connection.get_server_info()  # 5.5.57-0+deb8u1

        self.assertTrue(version.startswith('5.'), 'MySQL server should be from 5.x line')

    def test_tables(self):
        tables = list(self.connection.tables())
        print(tables)

        self.assertTrue('0000_the_table' in tables)

    def test_variables(self):
        variables = self.connection.variables()
        print(variables)

        self.assertTrue('version_compile_os' in variables)
        self.assertTrue('innodb_version' in variables)

    def test_variables_like(self):
        variables = self.connection.variables(like='innodb')
        print(variables)

        self.assertFalse('version_compile_os' in variables)  # this variable does not match given like
        self.assertTrue('innodb_version' in variables)

    def test_explain_query(self):
        """
        mysql> EXPLAIN SELECT * FROM 0000_the_table WHERE id = 2;
        +----+-------------+----------------+------+---------------+---------+---------+-------+------+-------------+
        | id | select_type | table          | type | possible_keys | key     | key_len | ref   | rows | Extra       |
        +----+-------------+----------------+------+---------------+---------+---------+-------+------+-------------+
        |  1 | SIMPLE      | 0000_the_table | ref  | PRIMARY,idx   | PRIMARY | 4       | const |    1 | Using index |
        +----+-------------+----------------+------+---------------+---------+---------+-------+------+-------------+
        1 row in set (0.00 sec)
        """
        res = list(self.connection.explain_query('SELECT * FROM 0000_the_table WHERE id = 2'))
        row = res[0]
        print(row)

        self.assertEqual(len(res), 1)
        self.assertEqual(row['key'], 'PRIMARY')
        self.assertEqual(row['table'], '0000_the_table')
        self.assertEqual(row['Extra'], 'Using index')

    def test_get_table_metadata(self):
        meta = self.connection.get_table_metadata('0000_the_table')
        print(meta)

        # stats
        self.assertEqual(meta['engine'], 'InnoDB')
        self.assertEqual(meta['rows'], 3)
        self.assertTrue(meta['index_size'] > 0)
        self.assertTrue(meta['data_size'] > 0)

        # columns
        self.assertTrue('id' in meta['columns'])
        self.assertTrue('id' in meta['columns'])
        self.assertTrue('foo' in meta['columns'])
        self.assertEqual(meta['columns']['id'], 'int(9)')
        self.assertEqual(len(meta['columns'].keys()), 2)

        # indices
        self.assertTrue('PRIMARY' in meta['indices'])
        self.assertTrue('idx_foo' in meta['indices'])
        self.assertEqual(meta['indices']['PRIMARY'], ['id', 'foo'])
        self.assertEqual(meta['indices']['idx_foo'], ['foo'])

        # assert False
