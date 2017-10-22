"""
This module contains utility functions and classes
"""
try:
    from urlparse import urlparse  # Python2
except ImportError:
    from urllib.parse import urlparse  # Python3


def parse_dsn(dsn):
    """
    Parser given Data Source Name string into an object that can be passed to a database connector.

    Example: mysql://alex:pwd@localhost/test
    DSN: <scheme>://<netloc>/<path>;<params>?<query>#<fragment>

    @see https://mysqlclient.readthedocs.io/user_guide.html#mysqldb

    :type dsn str
    :rtype: dict
    """
    parsed = urlparse(dsn)

    return {
        'host': parsed.hostname,
        'user': parsed.username,
        'passwd': parsed.password,
        'db': str(parsed.path).lstrip('/')
    }


class LinterEntry(object):
    """
    Wraps a single linter entry. Various formatters may display this data differently.
    """
    def __init__(self, linter_type, table_name, message, context=None):
        """
        :type linter_type str
        :type table_name str
        :type message str
        :type context dict
        """
        self.linter_type = linter_type
        self.table_name = table_name
        self.message = message
        self.context = context

    def __str__(self):
        return '{table_name}: {message}'.format(
            table_name=self.table_name, message=self.message)
