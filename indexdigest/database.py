"""
Database connector wrapper
"""
import logging
from collections import OrderedDict, defaultdict
from warnings import filterwarnings

import MySQLdb
from MySQLdb.cursors import DictCursor
from _mysql_exceptions import OperationalError

from indexdigest.schema import Column, Index
from indexdigest.utils import parse_dsn, memoize, IndexDigestError


class IndexDigestQueryError(IndexDigestError):
    """
    A wrapper for _mysql_exceptions.OperationalError:
    """
    pass


class DatabaseBase(object):
    """
    A generic wrapper of database connection with basic querying functionality.

    Sub-class this to mock database connection
    """

    def __init__(self, host, user, passwd, db):
        """
        Connects to a given database

        :type host str
        :type user str
        :type passwd str
        :type db str
        """
        self.logger = logging.getLogger(__name__)
        self.query_logger = logging.getLogger(__name__ + '.query')

        # lazy connect
        self._connection_params = dict(host=host, user=user, passwd=passwd, db=db)
        self._connection = None
        self.db_name = db

        # Suppress MySQL warnings when EXPLAIN is run (#63)
        filterwarnings('ignore', category=MySQLdb.Warning)

        # register queries
        self._queries = []

    @classmethod
    def connect_dsn(cls, dsn):
        """
        :type dsn str
        :rtype DatabaseBase
        """
        parsed = parse_dsn(dsn)
        return cls(**parsed)

    @property
    def connection(self):
        """
        Lazy connection

        :rtype: Connection
        """
        if self._connection is None:
            self.logger.info('Lazy connecting to %s and using %s database',
                             self._connection_params['host'], self._connection_params['db'])

            self._connection = MySQLdb.connect(**self._connection_params)

        return self._connection

    def get_queries(self):
        """
        :rtype: list[str]
        """
        return self._queries

    def query(self, sql, cursor_class=None):
        """
        :type sql str
        :type cursor_class MySQLdb.cursors.BaseCursor
        :rtype: MySQLdb.cursors.Cursor
        :raises IndexDigestQueryError
        """
        self.query_logger.info('%s', sql)

        cursor = self.connection.cursor(cursorclass=cursor_class)

        try:
            # Python 2: query should be bytes when executing %.
            # Python 3: query should be str (unicode) when executing %
            try:
                sql = sql.encode('utf8')
            except UnicodeDecodeError:
                pass

            cursor.execute(sql)
        except OperationalError as ex:
            (code, message) = ex.args  # e.g. (1054, "Unknown column 'test' in 'field list'")
            self.query_logger.error('Database error #%d: %s', code, message)
            raise IndexDigestQueryError(message)

        # register the query
        self._queries.append(sql)

        return cursor

    def query_row(self, sql):
        """
        :type sql str
        :rtype: list
        """
        return self.query(sql).fetchone()

    def query_dict_row(self, sql):
        """
        Return a single row as a dictionary

        :type sql str
        :rtype: dict
        """
        # DictCursor is a Cursor class that returns rows as dictionaries
        return self.query(sql, cursor_class=DictCursor).fetchone()

    def query_dict_rows(self, sql):
        """
        Return all rows as dictionaries

        :type sql str
        :rtype: dict[]
        """
        # DictCursor is a Cursor class that returns rows as dictionaries
        for row in self.query(sql, cursor_class=DictCursor):
            yield row

    def query_field(self, sql):
        """
        :type sql str
        :rtype: str
        """
        return self.query_row(sql)[0]

    def query_list(self, sql):
        """
        Returns an iterator with the first field on each row.

        e.g. SHOW TABLES

        :type sql str
        :rtype: list[str]
        """
        for row in self.query(sql):
            yield str(row[0])

    def query_key_value(self, sql):
        """
        Returns an ordered dictionary with key / value taken fro first two fields of each row.

        e.g. SHOW VARIABLES

        :type sql str
        :rtype: OrderedDict
        """
        res = OrderedDict()

        for row in self.query(sql):
            res[row[0]] = row[1]

        return res


class Database(DatabaseBase):
    """
    Database wrapper extended with some stats-related queries
    """

    @memoize
    def get_server_version(self):
        """
        Returns server version (e.g. "5.5.57-0+deb8u1")

        :rtype: str
        """
        return self.query_field('SELECT VERSION()')

    def get_server_hostname(self):
        """
        Return hostname of the server
        :rtype: str
        """
        return self.get_variables(like='hostname').get('hostname')

    @memoize
    def get_tables(self):
        """
        Returns the list of tables.

        :rtype: list[str]
        """
        return list(self.query_list('SHOW TABLES'))

    def get_variables(self, like=None):
        """
        Returns the key / value dictionary with server variables

        :type like str
        :rtype: OrderedDict
        """
        sql = 'SHOW VARIABLES'
        if like is not None:
            sql += ' LIKE "{}%"'.format(like)

        return self.query_key_value(sql)

    @memoize
    def explain_query(self, sql):
        """
        Runs EXPLAIN query for a given SQL

        :type sql str
        :rtype: list
        """
        # @see https://dev.mysql.com/doc/refman/5.7/en/explain-output.html
        return list(self.query_dict_rows('EXPLAIN {}'.format(sql)))

    def get_table_schema(self, table_name):
        """
        Run SHOW CREATE TABLE query for a given table
        :type table_name str
        :rtype: str
        """
        # @see https://dev.mysql.com/doc/refman/5.7/en/show-create-table.html
        return self.query_row('SHOW CREATE TABLE {}'.format(table_name))[1]

    def _get_information_schema_where(self, table_name):
        """
        :type table_name str
        :rtype: str
        """
        # @see https://dev.mysql.com/doc/refman/5.7/en/information-schema.html
        return "WHERE TABLE_SCHEMA='{db}' AND TABLE_NAME='{table_name}'".format(
            db=self._connection_params['db'], table_name=table_name)

    def get_table_metadata(self, table_name):
        """
        Return table's metadata

        :type table_name str
        :rtype: dict
        """
        # @see https://dev.mysql.com/doc/refman/5.7/en/tables-table.html
        stats = self.query_dict_row(
            "SELECT ENGINE, TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH "
            "FROM information_schema.TABLES " + self._get_information_schema_where(table_name))

        return {
            'engine': stats['ENGINE'],
            'rows': stats['TABLE_ROWS'],  # For InnoDB the row count is only a rough estimate
            'data_size': stats['DATA_LENGTH'],
            'index_size': stats['INDEX_LENGTH'],
        }

    @memoize
    def get_table_columns(self, table_name):
        """
        Return the list of indices for a given table

        :type table_name str
        :rtype: list[Column]
        """
        # @see https://dev.mysql.com/doc/refman/5.7/en/show-columns.html
        columns = [
            row['Field']
            for row in self.query_dict_rows("SHOW COLUMNS FROM {}".format(table_name))
        ]

        # @see https://dev.mysql.com/doc/refman/5.7/en/columns-table.html
        rows = self.query_dict_rows(
            "SELECT COLUMN_NAME as NAME, COLUMN_TYPE as TYPE, CHARACTER_SET_NAME, COLLATION_NAME "
            "FROM information_schema.COLUMNS " + self._get_information_schema_where(table_name))

        meta = dict()

        for row in rows:
            meta[row['NAME']] = Column(name=row['NAME'], column_type=row['TYPE'],
                                       character_set=row['CHARACTER_SET_NAME'],
                                       collation=row['COLLATION_NAME'])

        # keep the order taken from SHOW COLUMNS
        return [
            meta[column]
            for column in columns
        ]

    @memoize
    def get_table_indices(self, table_name):
        """
        Return the list of indices for a given table

        :type table_name str
        :rtype: list[Index]
        """
        # @see https://dev.mysql.com/doc/refman/5.7/en/statistics-table.html
        # @see https://dev.mysql.com/doc/refman/5.7/en/show-index.html
        res = self.query_dict_rows(
            "SELECT INDEX_NAME, NON_UNIQUE, SEQ_IN_INDEX, COLUMN_NAME, CARDINALITY " +
            "FROM information_schema.STATISTICS " + self._get_information_schema_where(table_name) +
            " ORDER BY INDEX_NAME, SEQ_IN_INDEX")

        index_columns = defaultdict(list)
        index_meta = OrderedDict()

        for row in res:
            index_name = row['INDEX_NAME']
            index_columns[index_name].append(row['COLUMN_NAME'])

            if index_name not in index_meta:
                index_meta[index_name] = {
                    'unique': int(row['NON_UNIQUE']) == 0,
                    'primary': row['INDEX_NAME'] == 'PRIMARY',
                }

        ret = []

        for index_name, meta in index_meta.items():
            columns = index_columns[index_name]
            ret.append(Index(
                name=index_name, columns=columns, primary=meta['primary'], unique=meta['unique']))

        return ret
