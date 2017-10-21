"""
This linter checks for redundant indices from a given set of them
"""


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
    :rtype: str
    """
    reports = []

    for table in database.tables():
        indices = database.get_table_indices(table)
        for (redundant_index, suggested_index) in get_redundant_indices(indices):
            # use LinterEntry wrapper
            reports.append('{}: {} index can be removed as redundant (covered by {})'.
                           format(table, redundant_index, suggested_index))

    return reports
