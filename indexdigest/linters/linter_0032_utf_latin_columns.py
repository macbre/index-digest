"""
This linter reports text columns that have characters encoding set to latin1
"""
from collections import OrderedDict

from indexdigest.utils import LinterEntry


def is_text_column_latin(column):
    """
    :type column indexdigest.schema.Column
    :rtype: bool
    """
    if not column.is_text_type():
        return False

    # ignore blob columns without specified character set
    if column.character_set is None:
        return False

    # ignore utf8 columns
    # utf8, ucs2, utf8mb4, utf16, utf16le, utf32
    # @see https://dev.mysql.com/doc/refman/5.7/en/charset-unicode.html
    if column.character_set.startswith('utf') or column.character_set in ['ucs2', 'binary']:
        return False

    return True


def check_latin_columns(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list[LinterEntry]
    """
    for table in database.get_tables():
        for column in database.get_table_columns(table):
            if not is_text_column_latin(column):
                continue

            # print([table, column, column.character_set, column.collation])

            context = OrderedDict()
            context['column'] = column.name
            context['column_character_set'] = column.character_set
            context['column_collation'] = column.collation
            context['schema'] = database.get_table_schema(table)

            yield LinterEntry(linter_type='non_utf_columns', table_name=table,
                              message='"{}" text column has "{}" character set defined'.
                              format(column.name, column.character_set),
                              context=context)
