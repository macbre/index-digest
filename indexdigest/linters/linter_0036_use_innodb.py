"""
This linter checks for ...
"""
from collections import OrderedDict

from indexdigest.utils import LinterEntry


def check_use_innodb(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list[LinterEntry]
    """
    res = database.query_dict_rows("SELECT table_name, engine FROM information_schema.tables "
                                   "WHERE engine <> 'InnoDB' and table_schema = '{}'".
                                   format(database.db_name))

    for row in res:
        context = OrderedDict()
        context['schema'] = database.get_table_schema(row['table_name'])
        context['engine'] = row['engine']

        yield LinterEntry(linter_type='use_innodb', table_name=row['table_name'],
                          message='"{table_name}" uses {engine} storage engine'.
                          format(**row),
                          context=context)
