"""index_digest

Analyses your database queries and schema and suggests indices improvements.

Usage:
  index_digest DSN [--sql-log=<file>] [--format=<formatter>]
  index_digest (-h | --help)
  index_digest --version

Options:
  DSN               Data Source Name of database to check
  --sql-log=<file>  Text file with SQL queries to check against the database
  --format=<formatter>  Use a given results formatter (plain, syslog, yaml)
  -h --help         Show this screen.
  --version         Show version.

Examples:
  index_digest mysql://username:password@localhost/dbname
  index_digest mysql://index_digest:qwerty@localhost/index_digest --sql-log=sql.log

Visit <https://github.com/macbre/index-digest>
"""
from __future__ import print_function

import logging
from itertools import chain
from os import getenv

from docopt import docopt

import indexdigest
from indexdigest.database import Database
from indexdigest.utils import IndexDigestError
from indexdigest.formatters import \
    format_plain, \
    format_syslog, \
    format_yaml
from indexdigest.linters import \
    check_queries_using_filesort, check_queries_using_temporary, \
    check_not_used_indices, check_queries_not_using_indices, \
    check_not_used_tables, check_not_used_columns, \
    check_redundant_indices, \
    check_full_table_scan, \
    check_latin_columns, \
    check_selects_with_like, \
    check_missing_primary_index, \
    check_test_tables, \
    check_insert_ignore_queries, \
    check_single_column


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
        check_missing_primary_index(database),
        check_test_tables(database),
        check_single_column(database),
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
            check_insert_ignore_queries(database, queries=queries),
        )

    # handle --format
    formatter = arguments.get('--format') or 'plain'
    logger.info("Using formatter: %s", formatter)

    if formatter == 'plain':
        print(format_plain(database, reports))
    elif formatter == 'syslog':
        ident = getenv('SYSLOG_IDENT', 'index-digest')
        logger.info('Using syslog ident: %s', ident)
        print(format_syslog(database, reports, ident))
    elif formatter == 'yaml':
        print(format_yaml(database, reports))
    else:
        raise IndexDigestError('Unknown formatter provided: {}'.format(formatter))
