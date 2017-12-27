# -*- coding: utf-8 -*-
"""
Provides --format=plain results formatter
"""
from sys import stdout

import indexdigest
from indexdigest.utils import LinterEntry

from termcolor import colored


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


def format_plain(database, reports, out=stdout):
    """
    :type database indexdigest.database.Database
    :type reports list
    :type out StringIO.StringIO
    """
    # cast to a list (to be able to count reports)
    reports = list(reports)

    # emit results
    line = '-' * 60 + "\n"

    out.write(line)
    out.write('Found {} issue(s) to report for "{}" database\n'.format(
        len(reports), database.db_name))
    out.write(line)
    out.write('MySQL v{} at {}\n'.format(
        database.get_server_version(), database.get_server_hostname()))
    out.write('index-digest v{}\n'.format(indexdigest.VERSION))
    out.write(line)

    if reports:
        for report in reports:
            assert isinstance(report, LinterEntry)

            out.write(
                colored(report.linter_type, color='blue', attrs=['bold']) +
                ' → table affected: ' +
                colored(report.table_name, attrs=['bold']) +
                '\n'
            )

            out.write(colored(
                '\n{} {}\n'.format(colored('✗', color='red', attrs=['bold']), report.message),
                color='white'))

            if report.context is not None:
                out.write('\n  {}\n'.format(format_context(report.context)))

            out.write('\n')
            out.write(line)

        out.write('Queries performed: {}\n'.format(len(database.get_queries())))
        # out.write('\n'.join(map(str, database.get_queries())))
    else:
        out.write('Jolly, good! No issues to report\n')
