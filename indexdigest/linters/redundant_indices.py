"""
This linter checks for redundant indices from a given set of them
"""
from . import LinterEntry


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
    reports = []

    for table in database.get_tables():
        indices = database.get_table_indices(table)
        for (redundant_index, suggested_index) in get_redundant_indices(indices):
            reports.append(
                LinterEntry(linter_type='redundant_indices', table_name=table,
                            message='{} index can be removed as redundant (covered by {})'.
                            format(redundant_index, suggested_index)))

    return reports
