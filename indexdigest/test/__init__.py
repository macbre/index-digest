from ..database import Database


class DatabaseTestMixin(object):
    DSN = 'mysql://index_digest:qwerty@localhost/index_digest'

    @property
    def connection(self):
        return Database.connect_dsn(self.DSN)


class DatabaseWithMockedRow(Database):

    def __init__(self, mocked_row):
        super(DatabaseWithMockedRow, self).__init__(db='', host='', passwd='', user='')
        self.row = mocked_row

    @property
    def connection(self):
        raise Exception('Class {} needs to mock the query_* method'.format(self.__class__.__name__))

    def query(self, sql, cursor=None):
        self.query_logger.info(sql)
        return [self.row]

    def query_row(self, sql):
        self.query_logger.info(sql)
        return self.row
