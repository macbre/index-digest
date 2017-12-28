"""
This linter checks for not used indices by going through SELECT queries
"""
import logging

from collections import defaultdict

from indexdigest.utils import LinterEntry, explain_queries


def check_not_used_indices(database, queries):
    """
    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    logger = logging.getLogger(__name__)

    used_indices = defaultdict(list)

    # EXPLAIN each query
    for (query, table_used, index_used, _) in explain_queries(database, queries):
        if index_used is not None:
            logger.info("Query <%s> uses %s index on `%s` table", query, index_used, table_used)
            used_indices[table_used].append(index_used)

    # analyze all tables used by the above queries
    # print(used_indices)
    for table_name in used_indices.keys():
        for index in database.get_table_indices(table_name):

            if index.name not in used_indices[table_name]:
                yield LinterEntry(linter_type='not_used_indices', table_name=table_name,
                                  message='"{}" index was not used by provided queries'.
                                  format(index.name),
                                  context={"not_used_index": str(index)})
