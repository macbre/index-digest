"""
This linter checks for redundant indices from a given set of them
"""
import logging

from collections import OrderedDict

from indexdigest.utils import LinterEntry


def get_redundant_indices(indices):
    """
    :type indices list[indexdigest.schema.Index]
    :rtype: list[tuple]
    """
    redundant_indices = []

    for index in indices:
        for compare in indices:
            if index.is_covered_by(compare):
                redundant_indices.append((index, compare, ))

    return redundant_indices


def check_redundant_indices(database):
    """
    :type database  indexdigest.database.Database
    :rtype: list[LinterEntry]
    """
    logger = logging.getLogger(__name__)

    for table in database.get_tables():
        logger.info("Checking %s table", table)

        indices = database.get_table_indices(table)
        meta = database.get_table_metadata(table)
        schema = database.get_table_schema(table)

        redundant_indices = set()

        for (redundant_index, suggested_index) in get_redundant_indices(indices):
            # the index we're about to suggest was reported as redundant - #48
            if suggested_index in redundant_indices:
                continue

            context = OrderedDict()
            context['redundant'] = str(redundant_index)
            context['covered_by'] = str(suggested_index)
            context['schema'] = schema
            context['table_data_size_mb'] = 1. * meta['data_size'] / 1024 / 1024
            context['table_index_size_mb'] = 1. * meta['index_size'] / 1024 / 1024

            # add to the list to avoid redundant indices being reported in a loop - #48
            redundant_indices.add(redundant_index)

            yield LinterEntry(linter_type='redundant_indices', table_name=table,
                              message='"{}" index can be removed as redundant (covered by "{}")'.
                              format(redundant_index.name, suggested_index.name),
                              context=context)
