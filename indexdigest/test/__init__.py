import logging

from ..database import Database

from unittest import TestCase


def read_queries_from_log(log_file):
    """
    :type log_file str
    :rtype: list[str]
    """
    with open('sql/{}'.format(log_file)) as fp:
        queries = fp.readlines()
        queries = list(map(str.strip, queries))  # remove trailing spaces

    return queries


class DatabaseTestMixin:
    DSN = 'mysql://index_digest:qwerty@127.0.0.1:53306/index_digest'
    DBNAME = 'index_digest'

    @property
    def connection(self):
        """
        :rtype: Database
        """
        return Database.connect_dsn(self.DSN)


class BigTableTest(TestCase, DatabaseTestMixin):

    ROWS = 100000  # how many rows to generate
    BATCH = 5000  # perform INSERT in batches

    BIG_TABLE_NAME = '0020_big_table'
    PREPARED = False

    def setUp(self):
        super(BigTableTest, self).setUp()

        # prepare the big table only once
        if not BigTableTest.PREPARED:
            self._prepare_big_table()
            BigTableTest.PREPARED = True

        assert self.table_populated(), 'Table 0020_big_table should be populated with values'

    def _rows(self):
        """
        Iterate from 1 to self.ROWS
        :rtype: list[int]
        """
        r = 0
        while r < self.ROWS:
            r += 1
            yield r

    @staticmethod
    def _insert_values(cursor, values):
        """
        :type cursor MySQLdb.cursors.BaseCursor
        :type values list[tuple]
        """
        if len(values) == 0:
            return

        # @see https://dev.mysql.com/doc/refman/5.7/en/insert.html
        cursor.executemany('INSERT INTO 0020_big_table(item_id,val,text,num) VALUES(%s,%s,%s,%s)', values)
        # print(values[0], cursor.lastrowid)

    def _prepare_big_table(self):
        """
        Fill the table with values
        """
        # @see http://www.mysqltutorial.org/python-mysql-insert/
        val = 1
        values = []

        # use the same connection through out the function
        connection = self.connection
        cursor = connection.connection.cursor()

        # is table already populated?
        if self.table_populated():
            return

        # no? populate it
        for row in self._rows():
            # Report low cardinality indices, use only a few distinct values (#31)
            num = row % 2

            values.append((row, val, '{:05x}'.format(row)[:5], num))

            if row % 5 == 0:
                val += 1

            if len(values) == self.BATCH:
                self._insert_values(cursor, values)
                values = []

        # insert any remaining values
        self._insert_values(cursor, values)

        # save changes to the database
        connection.connection.commit()

        cursor.close()

        # update key distribution statistics (#31)
        self.connection.query('ANALYZE TABLE 0020_big_table')

        cardinality_stats = self.connection.query_dict_rows(
            "select TABLE_NAME, INDEX_NAME, COLUMN_NAME, CARDINALITY from"
            " INFORMATION_SCHEMA.STATISTICS where"
            " TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = '{database_name}'".format(
                table_name=self.BIG_TABLE_NAME, database_name=self.DBNAME)
        )
        logging.warning('Big table initialized, cardinality: %r', list(cardinality_stats))

    def table_populated(self):
        """
        :rtype: bool
        """
        return self.connection.query_field('SELECT COUNT(*) FROM 0020_big_table') == self.ROWS


class DatabaseWithMockedRow(Database):

    def __init__(self, mocked_row):
        super(DatabaseWithMockedRow, self).__init__(db='', host='', passwd='', user='')
        self.row = mocked_row

    @property
    def connection(self):
        raise Exception('Class {} needs to mock the query_* method'.format(self.__class__.__name__))

    def query(self, sql, cursor=None):
        self._queries.append(sql)
        self.query_logger.info(sql)
        return [self.row]

    def query_row(self, sql):
        self._queries.append(sql)
        self.query_logger.info(sql)
        return self.row
