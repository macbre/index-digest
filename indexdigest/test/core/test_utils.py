from unittest import TestCase

from indexdigest.utils import parse_dsn


class TestUtils(TestCase):

    def test_parse_dsn(self):
        parsed = parse_dsn('mysql://alex:pwd@localhost/test')

        self.assertEqual('localhost', parsed['host'])
        self.assertEqual('alex', parsed['user'])
        self.assertEqual('pwd', parsed['passwd'])
        self.assertEqual('test', parsed['db'])
