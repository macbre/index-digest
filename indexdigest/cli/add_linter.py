"""
A helper script used to create files for new linter
"""
from __future__ import print_function

import logging
import re
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)-8s %(message)s',
)


def add_linter(linter_id, linter_name):
    """
    :type linter_id int
    :type linter_name str
    """
    logger = logging.getLogger('add_linter')

    # normalize values
    linter_id_fmt = '{:04d}'.format(linter_id)
    linter_name = re.sub(r'[^a-z]+', '-', linter_name.strip().lower())

    logger.info("Creating a new linter: %s - %s ...", linter_id_fmt, linter_name)

    # /sql directory
    sql_name = 'sql/{}-{}'.format(linter_id_fmt, linter_name.replace('_', '-'))
    logger.info("Add SQL schema and log files (%s) ...", sql_name)

    with open(sql_name + '.sql', 'wt') as file_name:
        # 0002_not_used_indices
        table_name = '{}_{}'.format(linter_id_fmt, linter_name.replace('-', '_'))

        file_name.writelines([
            '-- Report ...\n',
            '--\n',
            '-- https://github.com/macbre/index-digest/issues/{}\n'.format(linter_id),
            'DROP TABLE IF EXISTS `{}`;\n'.format(table_name),
            'CREATE TABLE `{}` (\n'.format(table_name),
            '-- \n',
            ');\n',
        ])

        logger.info('... %s created', file_name.name)

    with open(sql_name + '-log', 'wt') as file_name:
        file_name.writelines([
            '-- \n',
        ])

        logger.info('... %s created', file_name.name)

    # /indexdigest/linters directory
    linter_name = linter_name.replace('-', '_')
    logger.info("Add a Python code for %s linter ...", linter_name)

    with open('indexdigest/linters/linter_{}_{}.py'.
              format(linter_id_fmt, linter_name), 'wt') as file_name:
        file_name.writelines([
            '"""\n',
            'This linter checks for ...\n',
            '"""\n',
            'from collections import defaultdict\n',
            '\n',
            'from indexdigest.utils import LinterEntry, explain_queries\n',
            '\n',
            '\n',
            'def check_{}(database, queries):\n'.format(linter_name),
            '    """\n',
            '    :type database  indexdigest.database.Database\n',
            '    :type queries list[str]\n',
            '    :rtype: list[LinterEntry]\n',
            '    """\n',
            '    yield LinterEntry(linter_type=\'{}\', table_name=table_name,\n'.
            format(linter_name),
            '                      message=\'"{}" ...\'.\n',
            '                      format("foo"),\n',
            '                      context={"foo": str("bar")})\n',
        ])

        logger.info('... %s created', file_name.name)

    logger.info("Add a test ...")

    with open('indexdigest/test/linters/test_{}_{}.py'.format(linter_id_fmt, linter_name), 'wt') \
            as file_name:
        file_name.writelines([
            'from __future__ import print_function\n',
            '\n',
            'from unittest import TestCase\n',
            '\n',
            'from indexdigest.linters.linter_{0}_{1} import check_{1}\n'.
            format(linter_id_fmt, linter_name),
            'from indexdigest.test import DatabaseTestMixin, read_queries_from_log\n',
            '\n',
            '\n',
            'class TestLinter(TestCase, DatabaseTestMixin):\n',
            '\n',
            '    def test_{}(self):\n'.format(linter_name),
            '        pass\n',
        ])

        logger.info('... %s created', file_name.name)


def main():
    """
    usage: add_linter 89 empty_tables
    """
    try:
        linter_id = int(sys.argv[1])
        linter_name = str(sys.argv[2])

        add_linter(linter_id, linter_name)
    except IndexError:
        print('Usage: add_linter 89 empty_tables')
        exit(1)
