"""
Provides --format=plain results formatter
"""
import indexdigest
from indexdigest.utils import LinterEntry

from termcolor import colored, cprint


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


def format_plain(database, reports):
    """
    :type database indexdigest.database.Database
    :type reports list
    """
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
