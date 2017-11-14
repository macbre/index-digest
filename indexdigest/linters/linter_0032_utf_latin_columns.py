"""
This linter reports text columns that have characters encoding set to latin1
"""
from collections import OrderedDict

from indexdigest.utils import LinterEntry


def check_latin_columns(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list[LinterEntry]
    """
    for table in database.get_tables():
        for column in database.get_table_columns(table):
            if not column.is_text_type():
                continue

            # ignore utf8 columns
            if column.character_set in ['utf8']:
                continue

            # print([table, column, column.character_set, column.collation])

            context = OrderedDict()
            context['column'] = column.name
            context['column_character_set'] = column.character_set
            context['column_collation'] = column.collation

            yield LinterEntry(linter_type='non_utf_columns', table_name=table,
                              message='"{}" text column has "{}" character set defined'.
                              format(column.name, column.character_set),
                              context=context)
