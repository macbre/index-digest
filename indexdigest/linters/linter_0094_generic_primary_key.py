"""
This linter checks for ...
"""
from indexdigest.utils import LinterEntry

GENERIC_PRIMARY_KEY = 'id'


def check_generic_primary_key(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list[LinterEntry]
    """
    for table_name in database.get_tables():
        indices = [
            index for index in database.get_table_indices(table_name)
            if index.is_primary
        ]

        # no primary index, a different check will take care of it
        if not indices:
            continue

        # there can be only one primary key, take the first one from the list
        primary_key = indices[0]
        # print(table_name, primary_key, primary_key.columns[0])

        if primary_key.columns[0] == GENERIC_PRIMARY_KEY:
            yield LinterEntry(linter_type='generic_primary_key', table_name=table_name,
                              message='"{}" has a primary key called id, '
                                      'use a more meaningful name'.format(table_name),
                              context={"schema": database.get_table_schema(table_name)})
