# -*- coding: utf-8 -*-
"""index_digest

Analyses your database queries and schema and suggests indices improvements.

Usage:
  index_digest DSN [--sql-log=<file>]
  index_digest (-h | --help)
  index_digest --version

Options:
  DSN               Data Source Name of database to check
  --sql-log=<file>  Text file with SQL queries to check against the database
  -h --help         Show this screen.
  --version         Show version.

Examples:
  index_digest mysql://index_digest:qwerty@localhost/index_digest
  index_digest mysql://index_digest:qwerty@localhost/index_digest --sql-log=sql.log

Visit <https://github.com/macbre/index-digest>
"""
from __future__ import print_function, unicode_literals

import logging
from itertools import chain

from docopt import docopt
from termcolor import colored, cprint

import indexdigest
from indexdigest.database import Database
from indexdigest.utils import LinterEntry
from indexdigest.linters import \
    check_queries_using_filesort, check_queries_using_temporary, \
    check_not_used_indices, check_queries_not_using_indices, \
    check_not_used_tables, check_not_used_columns, \
    check_redundant_indices, \
    check_full_table_scan, \
    check_latin_columns, \
    check_selects_with_like


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


def main():
    """ Main entry point for CLI"""
    logger = logging.getLogger(__name__)

    arguments = docopt(__doc__, version='index_digest {}'.format(indexdigest.VERSION))
    logger.debug('Options: %s', arguments)

    if 'DSN' not in arguments:
        return

    # connect to the database
    database = Database.connect_dsn(arguments['DSN'])
    logger.debug('Connected to MySQL server v%s', database.get_server_version())

    # read SQL log file (if provided)
    sql_log = arguments.get('--sql-log')
    if sql_log:
        logger.debug('Trying to open SQL log file: %s', sql_log)

        with open(sql_log) as log_file:
            queries = log_file.readlines()
            queries = list(map(str.strip, queries))  # remove trailing spaces
            logger.debug('Got %d entries in SQL log file', len(queries))
    else:
        queries = None

    # run all checks
    reports = chain(
        check_redundant_indices(database),
        check_latin_columns(database),
    )

    # checks that use SQL log
    if queries:
        reports = chain(
            reports,
            check_not_used_indices(database, queries=queries),
            check_not_used_tables(database, queries=queries),
            check_not_used_columns(database, queries=queries),
            check_queries_not_using_indices(database, queries=queries),
            check_queries_using_filesort(database, queries=queries),
            check_queries_using_temporary(database, queries=queries),
            check_full_table_scan(database, queries=queries),
            check_selects_with_like(database, queries=queries),
        )

    # cast to a list (to be able to count reports)
    reports = list(reports)

    # emit results
    line = '-' * 60

    print(line)
    print('Found {} issue(s) to report for "{}" database'.format(len(reports), database.db_name))
    print(line)
    print('MySQL v{} at {}'.format(database.get_server_version(), database.get_server_hostname()))
    print('index-digest v{}'.format(indexdigest.VERSION))
    print(line)

    # TODO: implement formatters
    if reports:
        for report in reports:
            assert isinstance(report, LinterEntry)

            print(
                colored(report.linter_type, color='blue', attrs=['bold']) +
                ' → table affected: ' +
                colored(report.table_name, attrs=['bold'])
            )

            cprint(
                '\n{} {}'.format(colored('✗', color='red', attrs=['bold']), report.message),
                color='white')

            if report.context is not None:
                print('\n  ' + format_context(report.context))

            print()
            print(line)

        print('Queries performed: {}'.format(len(database.get_queries())))
        # print('\n'.join(map(str, database.get_queries())))
    else:
        print('Jolly, good! No issues to report')
