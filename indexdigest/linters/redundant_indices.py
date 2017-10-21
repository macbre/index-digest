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
