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
    # in MySQL 8.0 information_schema tables columns are uppercase
    res = database.query_dict_rows("SELECT TABLE_NAME, ENGINE FROM information_schema.tables "
                                   "WHERE ENGINE <> 'InnoDB' and TABLE_SCHEMA = '{}'".
                                   format(database.db_name))

    for row in res:
        context = OrderedDict()
        context['schema'] = database.get_table_schema(row['TABLE_NAME'])
        context['engine'] = row['ENGINE']

        yield LinterEntry(linter_type='use_innodb', table_name=row['TABLE_NAME'],
                          message='"{TABLE_NAME}" uses {ENGINE} storage engine'.
                          format(**row),
                          context=context)
