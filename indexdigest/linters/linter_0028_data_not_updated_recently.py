"""
This linter looks for table that were not updated recently
"""
from collections import OrderedDict
from datetime import datetime
from time import time

from indexdigest.utils import LinterEntry

from .linter_0028_data_too_old import get_time_columns, get_boundary_times


def check_data_not_updated_recently(database, env=None):
    """
    :type database  indexdigest.database.Database
    :type env dict
    :rtype: list[LinterEntry]
    """
    now = int(time())  # I will probably never understand dates handling in Python

    # set up a diff threshold (in days)
    env = env if env else dict()
    diff_threshold = env.get('INDEX_DIGEST_DATA_NOT_UPDATED_RECENTLY_THRESHOLD_DAYS', 30)

    for (table_name, column) in get_time_columns(database):
        timestamps = get_boundary_times(database, table_name, column)
        if timestamps is None:
            continue

        diff = now - timestamps.get('max')
        print(table_name, column, timestamps, now, diff)

        if diff > diff_threshold * 86400:
            diff_days = int(diff / 86400)

            context = OrderedDict()
            context['diff_days'] = diff_days
            context['data_since'] = datetime.fromtimestamp(timestamps.get('min'))
            context['data_until'] = datetime.fromtimestamp(timestamps.get('max'))
            context['rows'] = database.get_table_rows_estimate(table_name)
            context['schema'] = database.get_table_schema(table_name)

            yield LinterEntry(linter_type='data_not_updated_recently', table_name=table_name,
                              message='"{}" has the latest row added {} days ago, '
                                      'consider checking if it should be up-to-date'.
                              format(table_name, diff_days),
                              context=context)
