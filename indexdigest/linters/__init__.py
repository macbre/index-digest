"""
Contains linters used to check the database for improvements.
"""
# expose linters
from .linter_0002_not_used_indices import check_not_used_indices
from .linter_0004_redundant_indices import check_redundant_indices
from .linter_0006_not_used_columns_and_tables import check_not_used_tables, check_not_used_columns
from .linter_0019_queries_not_using_indices import check_queries_not_using_indices
from .linter_0020_filesort_temporary_table import \
    check_queries_using_filesort, check_queries_using_temporary
from .linter_0026_full_table_scan import check_full_table_scan
from .linter_0027_selects_with_like import check_selects_with_like
from .linter_0032_utf_latin_columns import check_latin_columns
