"""
This linter reports missing primary / unique index
"""
from collections import OrderedDict

from indexdigest.utils import LinterEntry


def check_missing_primary_index(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list[LinterEntry]
    """
    for table in database.get_tables():
        # list non-primary (and non-unique) indices only
        # @see https://bugs.mysql.com/bug.php?id=76252
        # @see https://github.com/Wikia/app/pull/9863
        indices = [
            index for index in database.get_table_indices(table)
            if index.is_primary or index.is_unique
        ]

        if indices:
            # so we have at least one primary or unique index defined
            continue

        context = OrderedDict()
        context['schema'] = database.get_table_schema(table)

        yield LinterEntry(linter_type='missing_primary_index', table_name=table,
                          message='"{}" table does not have any primary or unique index'.
                          format(table),
                          context=context)
