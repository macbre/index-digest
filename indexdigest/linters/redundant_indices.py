"""
This linter checks for redundant indices from a given set of them
"""
import logging

from collections import OrderedDict

from indexdigest.utils import LinterEntry


def get_redundant_indices(indices):
    """
    :type indices list[indexdigest.indices.Index]
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
    reports = []

    for table in database.get_tables():
        logger.info("Checking %s table", table)

        indices = database.get_table_indices(table)
        meta = database.get_table_metadata(table)
        schema = database.get_table_schema(table)

        for (redundant_index, suggested_index) in get_redundant_indices(indices):
            context = OrderedDict()
            context['redundant'] = redundant_index
            context['covered_by'] = suggested_index
            context['schema'] = schema
            context['table_data_size_mb'] = 1. * meta['data_size'] / 1024 / 1024
            context['table_index_size_mb'] = 1. * meta['index_size'] / 1024 / 1024

            reports.append(
                LinterEntry(linter_type='redundant_indices', table_name=table,
                            message='{} index can be removed as redundant (covered by {})'.
                            format(redundant_index, suggested_index),
                            context=context))

    return reports
