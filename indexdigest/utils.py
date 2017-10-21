"""
This module contains utility functions
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
