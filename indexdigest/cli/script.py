"""index_digest

Analyses your database queries and schema and suggests indices improvements.

Usage:
  index_digest DSN
  index_digest (-h | --help)
  index_digest --version

Options:
  DSN               Data Source Name of database to check
  -h --help         Show this screen.
  --version         Show version.

Examples:
  index_digest mysql://index_digest:qwerty@localhost/index_digest

Visit <https://github.com/macbre/index-digest>
"""
from __future__ import print_function

import logging
from docopt import docopt

import indexdigest
from indexdigest.database import Database
from indexdigest.linters import check_redundant_indices


def main():
    """ Main entry point for CLI"""
    logger = logging.getLogger(__name__)

    arguments = docopt(__doc__, version='index_digest {}'.format(indexdigest.VERSION))
    logger.debug('Options: %s', arguments)

    if 'DSN' not in arguments:
        return

    # connect to thhe database
    database = Database.connect_dsn(arguments['DSN'])
    logger.debug('Connected to MySQL server v%s', database.get_server_info())

    # run all checks
    reports = check_redundant_indices(database)

    # emit results
    print('Found {} issue(s) to report for "{}" database'.format(len(reports), database.db_name))

    # TODO: implement formatters
    for report in reports:
        print('{} | {}'.format(report.linter_type, str(report)))
