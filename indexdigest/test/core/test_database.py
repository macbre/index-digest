from unittest import TestCase

from indexdigest.database import Database


class TestUtils(TestCase):

    DSN = 'mysql://index_digest:qwerty@localhost/index_digest'

    def test_database_connect(self):
        conn = Database(host='localhost', user='index_digest', passwd='qwerty', db='index_digest')
        self.assertIsInstance(conn, Database)

    def test_database_connect_dsn(self):
        conn = Database.connect_dsn(self.DSN)
        self.assertIsInstance(conn, Database)

    def test_database_version(self):
        conn = Database.connect_dsn(self.DSN)
        version = conn.get_server_info()  # 5.5.57-0+deb8u1

        self.assertTrue(version.startswith('5.'), 'MySQL server should be from 5.x line')
