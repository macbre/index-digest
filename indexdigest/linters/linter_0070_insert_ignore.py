"""
This linter checks INSERT IGNORE queries

If you use the IGNORE modifier, errors that occur while executing the INSERT statement are ignored.
For example, without IGNORE, a row that duplicates an existing UNIQUE index or PRIMARY KEY value
in the table causes a duplicate-key error and the statement is aborted. With IGNORE, the row is
discarded and no error occurs. Ignored errors generate warnings instead.

Data conversions that would trigger errors abort the statement if IGNORE is not specified.
With IGNORE, invalid values are adjusted to the closest values and inserted; warnings
are produced but the statement does not abort.

@see https://medium.com/legacy-systems-diary/things-to-avoid-episode-1-insert-ignore-535b4c24406b
"""
import re

from collections import OrderedDict
from sql_metadata import get_query_tables

from indexdigest.utils import LinterEntry, shorten_query


def remove_comments(sql):
    """
    :type sql str
    :rtype: str
    """
    return re.sub(r'/\*[^*]+\*/', '', sql)


def is_insert_ignore_query(sql):
    """
    :type sql str
    :rtype: bool
    """
    sql = remove_comments(sql).lstrip()
    return re.match(r'^INSERT\s+IGNORE\s', sql, flags=re.IGNORECASE) is not None


def check_insert_ignore_queries(database, queries):
    """
    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    queries = [query for query in queries if is_insert_ignore_query(query)]

    for query in queries:
        table_used = get_query_tables(query)[0]

        context = OrderedDict()
        context['query'] = query
        context['schema'] = database.get_table_schema(table_used)

        yield LinterEntry(linter_type='insert_ignore', table_name=table_used,
                          message='"{}" query uses a risky INSERT IGNORE'.
                          format(shorten_query(query)),
                          context=context)
