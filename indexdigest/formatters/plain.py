# -*- coding: utf-8 -*-
"""
Provides --format=plain results formatter
"""
from termcolor import colored

import indexdigest
from indexdigest.utils import LinterEntry


def format_context(context):
    """
    :type context dict
    :rtype: str
    """
    return '\n  '.join([
        "- {key}: {value}".format(
            key=colored(key, color='green', attrs=['bold']),
            value=str(value).replace("\n", "\n    ")
        )
        for (key, value) in context.items()
    ])


def format_plain(database, reports):
    """
    :type database indexdigest.database.Database
    :type reports list
    :rtype: str
    """
    out = ''

    # cast to a list (to be able to count reports)
    reports = list(reports)

    # emit results
    line = '-' * 60 + "\n"

    out += line
    out += 'Found {} issue(s) to report for "{}" database\n'.format(
        len(reports), database.db_name)
    out += line
    out += 'MySQL v{} at {}\n'.format(
        database.get_server_version(), database.get_server_hostname())
    out += 'index-digest v{}\n'.format(indexdigest.VERSION)
    out += line

    if reports:
        for report in reports:
            assert isinstance(report, LinterEntry)

            out += colored(report.linter_type, color='blue', attrs=['bold']) + \
                ' → table affected: ' + \
                colored(report.table_name, attrs=['bold']) + \
                '\n'

            out += colored(
                '\n{} {}\n'.format(colored('✗', color='red', attrs=['bold']), report.message),
                color='white')

            if report.context is not None:
                out += '\n  {}\n'.format(format_context(report.context))

            out += '\n'
            out += line

        out += 'Queries performed: {}'.format(len(database.get_queries()))
        # out += '\n'.join(map(str, database.get_queries())))
    else:
        out += 'Jolly, good! No issues to report'

    return out
