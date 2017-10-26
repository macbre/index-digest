"""
Contains linters used to check the database for improvements.
"""
# expose linters
from .not_used_columns_and_tables import check_not_used_tables, check_not_used_columns
from .not_used_indices import check_not_used_indices, check_queries_not_using_indices
from .redundant_indices import check_redundant_indices
