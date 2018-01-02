"""
Provides --format=syslog results formatter - pushes JSON messages via syslog
"""
from __future__ import absolute_import

import json
import syslog

from collections import OrderedDict

import indexdigest


def format_report(database, report):
    """
    :type database indexdigest.database.Database
    :type report indexdigest.utils.LinterEntry
    :rtype: str
    """
    res = OrderedDict()

    res['appname'] = 'index-digest'

    res['meta'] = OrderedDict()
    res['meta']['version'] = 'index-digest v{}'.format(indexdigest.VERSION)
    res['meta']['database_name'] = database.db_name
    res['meta']['database_host'] = database.get_server_hostname()
    res['meta']['database_version'] = 'MySQL v{}'.format(database.get_server_version())

    res['report'] = OrderedDict()
    res['report']['type'] = report.linter_type
    res['report']['table'] = report.table_name
    res['report']['message'] = report.message

    if report.context:
        res['report']['context'] = report.context

    return json.dumps(res)


def format_syslog(database, reports, ident='index-digest'):
    """
    :type database indexdigest.database.Database
    :type reports list
    :type ident str
    :rtype: str
    """
    syslog.openlog(ident=ident, logoption=syslog.LOG_PID, facility=syslog.LOG_USER)

    for report in reports:
        syslog.syslog(format_report(database, report))

    syslog.closelog()
    return ''
