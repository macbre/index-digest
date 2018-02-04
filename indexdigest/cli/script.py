"""index_digest

Analyses your database queries and schema and suggests indices improvements.

Usage:
  index_digest DSN [--sql-log=<file>] [--format=<formatter>] [--analyze-data]
  index_digest (-h | --help)
  index_digest --version

Options:
  DSN               Data Source Name of database to check
  --sql-log=<file>  Text file with SQL queries to check against the database
  --format=<formatter>  Use a given results formatter (plain, syslog, yaml)
  --analyze-data    Run additional checks that will query table data (can be slow!)
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
from os import getenv, environ

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
    check_single_column, \
    check_empty_tables, \
    check_select_star, \
    check_having_clause, \
    check_data_too_old, \
    check_data_not_updated_recently


def get_reports(database, sql_log=None, analyze_data=False):
    """
    :type database Database
    :type sql_log str
    :type analyze_data bool
    :rtype: list[LinterEntry]
    """
    logger = logging.getLogger(__name__)

    # read SQL log file (if provided)
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
        check_empty_tables(database),
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
            check_select_star(database, queries=queries),
            check_having_clause(database, queries=queries),
        )

    # checks that require --analyze-data switch to be on (see #28)
    if analyze_data is True:
        logger.info("Will run data analyzing checks, can take a while...")

        reports = chain(
            reports,
            check_data_too_old(database, env=environ),
            check_data_not_updated_recently(database, env=environ),
        )

    return reports


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

    reports = get_reports(
        database,
        sql_log=arguments.get('--sql-log'),
        analyze_data=arguments.get('--analyze-data')
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
