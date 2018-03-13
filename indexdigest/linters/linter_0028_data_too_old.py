"""
This linter looks for tables that have really old data
"""
from collections import OrderedDict
from datetime import datetime
from time import time

from indexdigest.utils import LinterEntry, memoize


def get_time_columns(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list
    """
    for table_name in database.get_tables():
        time_columns = [
            column
            for column in database.get_table_columns(table_name)
            if column.is_timestamp_type() or 'time' in column.name
        ]

        # there are no time type columns, skip
        if not time_columns:
            continue

        # for now just check the first time column
        yield (table_name, time_columns[0])


@memoize
def get_boundary_times(database, table_name, column):
    """
    :type database  indexdigest.database.Database
    :type table_name str
    :type column indexdigest.Column.column
    :rtype: dict
    """
    # this may take a while when {column} is not indexed!
    query = 'SELECT /* index-digest */ UNIX_TIMESTAMP(MIN(`{column}`)) as `min`, ' \
            'UNIX_TIMESTAMP(MAX(`{column}`)) as `max` FROM `{table}`'.\
        format(
            column=column.name,
            table=table_name
        )

    timestamps = database.query_dict_row(query)

    # if there's no data in the table, return None
    return timestamps if timestamps.get('min') and timestamps.get('max') else None


def check_data_too_old(database, env=None):
    """
    :type database  indexdigest.database.Database
    :type env dict
    :rtype: list[LinterEntry]
    """
    now = int(time())  # I will probably never understand dates handling in Python

    # set up a diff threshold (in days)
    env = env if env else dict()
    diff_threshold = int(env.get('INDEX_DIGEST_DATA_TOO_OLD_THRESHOLD_DAYS', 3 * 30))

    for (table_name, column) in get_time_columns(database):
        timestamps = get_boundary_times(database, table_name, column)

        if timestamps is None or timestamps.get('min') is None:
            continue

        diff = now - timestamps.get('min')
        # print(table_name, column, timestamps, now, diff)

        if diff > diff_threshold * 86400:
            diff_days = int(diff / 86400)

            metadata = database.get_table_metadata(table_name)

            context = OrderedDict()
            context['diff_days'] = diff_days
            context['data_since'] = str(datetime.fromtimestamp(timestamps.get('min')))
            context['data_until'] = str(datetime.fromtimestamp(timestamps.get('max')))
            context['date_column_name'] = str(column)
            context['schema'] = database.get_table_schema(table_name)
            context['rows'] = database.get_table_rows_estimate(table_name)
            context['table_size_mb'] = \
                1. * (metadata['data_size'] + metadata['index_size']) / 1024 / 1024

            yield LinterEntry(linter_type='data_too_old', table_name=table_name,
                              message='"{}" has rows added {} days ago, '
                                      'consider changing retention policy'.
                              format(table_name, diff_days),
                              context=context)
