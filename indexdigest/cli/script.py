# pylint: disable=line-too-long
"""index_digest

Analyses your database queries and schema and suggests indices improvements.

Usage:
  index_digest DSN [--sql-log=<file>] [--format=<formatter>] [--analyze-data] [--checks=<checks> | --skip-checks=<skip-checks>] [--tables=<tables> | --skip-tables=<skip-tables>]
  index_digest (-h | --help)
  index_digest --version

Options:
  DSN               Data Source Name of database to check
  --sql-log=<file>  Text file with SQL queries to check against the database
  --format=<formatter>  Use a given results formatter (plain, syslog, yaml)
  --analyze-data    Run additional checks that will query table data (can be slow!)
  --checks=<list>   Comma-separated lists of checks to report
  --skip-checks=<list> Comma-separated lists of checks to skip from report
  --tables=<list>   Comma-separated lists of tables to report
  --skip-tables=<list> Comma-separated lists of tables to skip from report
  -h --help         Show this screen.
  --version         Show version.

Examples:
  index_digest mysql://username:password@localhost/dbname
  index_digest mysql://index_digest:qwerty@localhost/index_digest --sql-log=sql.log
  index_digest mysql://index_digest:qwerty@localhost/index_digest --skip-checks=non_utf_columns
  index_digest mysql://index_digest:qwerty@localhost/index_digest --analyze-data --checks=data_too_old,data_not_updated_recently
  index_digest mysql://index_digest:qwerty@localhost/index_digest --analyze-data --skip-tables=DATABASECHANGELOG,DATABASECHANGELOGLOCK

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
    check_data_not_updated_recently, \
    check_generic_primary_key, \
    check_high_offset_selects, \
    check_use_innodb


def get_reports(database, sql_log=None, analyze_data=False):
    """
    :type database Database
    :type sql_log str
    :type analyze_data bool
    :rtype: list[indexdigest.utils.LinterEntry]
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
        check_generic_primary_key(database),
        check_use_innodb(database),
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
            check_high_offset_selects(database, queries=queries),
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


def filter_reports_by_type(reports, checks=None, skip_checks=None):
    """
    :type reports list[indexdigest.utils.LinterEntry]
    :type checks str
    :type skip_checks str
    :rtype: list[indexdigest.utils.LinterEntry]
    """
    if checks:
        return [
            report for report in reports
            if report.linter_type in checks.split(',')
        ]

    if skip_checks:
        return [
            report for report in reports
            if report.linter_type not in skip_checks.split(',')
        ]

    return reports


def filter_reports_by_table(reports, tables=None, skip_tables=None):
    """
    :type reports list[indexdigest.utils.LinterEntry]
    :type tables str
    :type skip_tables str
    :rtype: list[indexdigest.utils.LinterEntry]
    """
    if tables:
        return [
            report for report in reports
            if report.table_name in tables.split(',')
        ]

    if skip_tables:
        return [
            report for report in reports
            if report.table_name not in skip_tables.split(',')
        ]

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

    # handle --checks / --skip-checks
    reports = filter_reports_by_type(
        reports,
        checks=arguments.get('--checks'),
        skip_checks=arguments.get('--skip-checks')
    )

    # handle --tables / --skip-tables
    reports = filter_reports_by_table(
        reports,
        tables=arguments.get('--tables'),
        skip_tables=arguments.get('--skip-tables')
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
