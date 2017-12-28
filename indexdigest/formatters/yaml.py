"""
Provides --format=yaml results formatter
"""
from __future__ import absolute_import

from collections import OrderedDict

import yaml
import yamlordereddictloader

import indexdigest


def format_report(report):
    """
    :type report indexdigest.utils.LinterEntry
    :rtype: OrderedDict
    """
    res = OrderedDict()

    res['type'] = report.linter_type
    res['table'] = report.table_name
    res['message'] = report.message

    if report.context:
        res['context'] = report.context

    return res


def format_yaml(database, reports):
    """
    :type database indexdigest.database.Database
    :type reports list
    :rtype: str
    """
    report = OrderedDict()

    report['meta'] = OrderedDict()
    report['meta']['version'] = 'index-digest v{}'.format(indexdigest.VERSION)
    report['meta']['database_name'] = database.db_name
    report['meta']['database_host'] = database.get_server_hostname()
    report['meta']['database_version'] = 'MySQL v{}'.format(database.get_server_version())

    report['reports'] = [format_report(item) for item in reports]

    return yaml.dump(report,
                     Dumper=yamlordereddictloader.Dumper,
                     default_flow_style=False,
                     explicit_start=True,
                     explicit_end=True)
