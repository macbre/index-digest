"""
This linter checks for not used indices by going through SELECT queries
"""
import logging

from collections import defaultdict

from indexdigest.utils import LinterEntry, is_select_query


def check_not_used_indices(database, queries):
    """
    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    logger = logging.getLogger(__name__)

    # analyze only SELECT queries from the log
    queries = filter(is_select_query, queries)
    used_indices = defaultdict(list)

    # generate reports
    reports = []

    # EXPLAIN each query
    for query in queries:
        for row in database.explain_query(query):
            table_used = row['table']
            index_used = row['key']

            if index_used is not None:
                logger.info("Query <%s> uses %s index on `%s` table", query, index_used, table_used)
                used_indices[table_used].append(index_used)
            else:
                logger.warning("Query <%s> does not use any index on `%s` table", query, table_used)

            # print(query, table_used, index_used)

    # print(used_indices)

    # analyze all tables used by the above queries
    for table_name in used_indices.keys():
        for index in database.get_table_indices(table_name):

            if index.name not in used_indices[table_name]:
                reports.append(
                    LinterEntry(linter_type='not_used_indices', table_name=table_name,
                                message='"{}" was not used by provided queries'.format(str(index)),
                                context={"not_used_index": index}))

    return reports
