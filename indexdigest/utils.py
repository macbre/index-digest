"""
This module contains utility functions and classes
"""
from urllib.parse import urlparse

import functools
import logging
import re


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
        'port': int(parsed.port) if parsed.port else 3306,
        'user': parsed.username,
        'passwd': parsed.password,
        'db': str(parsed.path).lstrip('/')
    }


def is_select_query(query):
    """
    :type query str
    :rtype bool
    """
    query = query.lstrip().lower()
    query = re.sub(r'^/\*[^*]+\*/', '', query)  # remove SQL comments

    return query.lstrip().startswith('select')


def explain_queries(database, queries):
    """
    Yields EXPLAIN result rows for given queries

    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: tuple[str,str,str,str]
    """
    # analyze only SELECT queries from the log
    for query in filter(is_select_query, queries):
        try:
            for row in database.explain_query(query):
                table_used = row['table']
                index_used = row['key']

                yield (query, table_used, index_used, row)
        except IndexDigestError:
            logger = logging.getLogger('explain_queries')
            logger.error('Cannot explain the query: %s', query)


def shorten_query(query, max_len=50):
    """
    :type query str
    :type max_len int
    :rtype: str
    """
    query = query.rstrip('; ')
    return '{}...'.format(query[:max_len]) if len(query) > max_len else query


def memoize(func):
    """
    Memoization pattern implemented

    :type func
    :rtype func
    """
    # @see https://medium.com/@nkhaja/memoization-and-decorators-with-python-32f607439f84
    cache = func.cache = {}

    @functools.wraps(func)
    def memoized_func(*args, **kwargs):
        """
        :type args
        :type kwargs
        """
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return memoized_func


# pylint:disable=too-few-public-methods
class LinterEntry:
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


class IndexDigestError(Exception):
    """
    index-digest base exception class
    """
