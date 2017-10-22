"""
Contains linters used to check the database for improvements.
"""
# expose linters
from .not_used_columns_and_tables import check_not_used_tables
from .redundant_indices import check_redundant_indices
