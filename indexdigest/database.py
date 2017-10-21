"""
Database connector wrapper
"""
import logging
from collections import OrderedDict

import MySQLdb

from indexdigest.utils import parse_dsn


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
        self.logger = logging.getLogger(self.__class__.__name__)

        # lazy connect
        self._connection_params = dict(host=host, user=user, passwd=passwd, db=db)
        self._connection = None

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

    def query(self, sql):
        """
        :type sql str
        :rtype: MySQLdb.cursors.Cursor
        """
        self.logger.info('Query: %s', sql)

        cursor = self.connection.cursor()
        cursor.execute(sql)

        return cursor

    def query_row(self, sql):
        """
        :type sql str
        :rtype: list
        """
        cursor = self.query(sql)

        return cursor.fetchone()

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
        :rtype: str[]
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

    def get_server_info(self):
        """
        Returns server version (e.g. "5.5.57-0+deb8u1")

        :rtype: str
        """
        return self.query_field('SELECT VERSION()')

    def tables(self):
        """
        Returns an iterator with the list of tables.

        :rtype: str[]
        """
        return self.query_list('SHOW TABLES')

    def variables(self, like=None):
        """
        Returns the key / value dictionary with server variables

        :type like str
        :rtype: OrderedDict
        """
        sql = 'SHOW VARIABLES'
        if like is not None:
            sql += ' LIKE "{}%"'.format(like)

        return self.query_key_value(sql)
