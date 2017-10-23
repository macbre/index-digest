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
from __future__ import print_function

import json
import logging
from docopt import docopt

import indexdigest
from indexdigest.database import Database
from indexdigest.linters import \
    check_not_used_tables, check_not_used_columns, \
    check_redundant_indices


def format_context(context):
    """
    :type context dict
    :rtype: str
    """
    if context is None:
        return 'n/a'

    return '\n\t'.join([
        "- {}: {}".format(key, str(value).replace("\n", "\n\t  ")) for (key, value) in context.items()
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
    logger.debug('Connected to MySQL server v%s', database.get_server_info())

    # read SQL log file (if provided)
    sql_log = arguments.get('--sql-log')
    if sql_log:
        logger.debug('Trying to open SQL log file: %s', sql_log)

        with open(sql_log) as log_file:
            queries = log_file.readlines()
            logger.debug('Got %d entries in SQL log file', len(queries))
    else:
        queries = None

    # run all checks
    reports = check_redundant_indices(database)

    if queries:
        reports += check_not_used_tables(database, queries=queries)
        reports += check_not_used_columns(database, queries=queries)

    # emit results
    line = '-' * 120

    print(line)
    print('Found {} issue(s) to report for "{}" database'.format(len(reports), database.db_name))
    print(line)

    # TODO: implement formatters
    if reports:
        for report in reports:
            print('{} / {}\n\n\t{}\n\n\t{}'.format(
                report.linter_type, report.table_name, report.message,
                format_context(report.context)
            ))
            print(line)
    else:
        print('Jolly, good! No issues to report')
