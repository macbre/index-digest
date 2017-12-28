"""
Provides --format=yaml results formatter
"""
from collections import OrderedDict

import yaml
import yamlordereddictloader

import indexdigest
from indexdigest.schema import Index


def index_representer(dumper, data):
    """
    Provides a custom YAML formatter for indexdigest.schema.Index class
    """
    return dumper.represent_scalar('!index', str(data))


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

    report['reports'] = [format_report(report) for report in reports]

    # @see http://pyyaml.org/wiki/PyYAMLDocumentation
    yaml.add_representer(Index, index_representer)

    return yaml.dump(report,
                     Dumper=yamlordereddictloader.Dumper,
                     default_flow_style=False,
                     explicit_start=True,
                     explicit_end=True)
