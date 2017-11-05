"""
This linter checks for not used indices by going through SELECT queries
"""
import logging

from collections import defaultdict, OrderedDict

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

    # generate reports
    reports = []

    # analyze all tables used by the above queries
    # print(used_indices)
    for table_name in used_indices.keys():
        for index in database.get_table_indices(table_name):

            if index.name not in used_indices[table_name]:
                reports.append(
                    LinterEntry(linter_type='not_used_indices', table_name=table_name,
                                message='"{}" index was not used by provided queries'.
                                format(index.name),
                                context={"not_used_index": index}))

    return reports


def check_queries_not_using_indices(database, queries):
    """
    :type database  indexdigest.database.Database
    :type queries list[str]
    :rtype: list[LinterEntry]
    """
    reports = []

    for (query, table_used, index_used, explain_row) in explain_queries(database, queries):
        # print(query, explain_row)

        if index_used is None:
            context = OrderedDict()
            context['query'] = query

            # https://dev.mysql.com/doc/refman/5.7/en/explain-output.html#explain-extra-information
            context['explain_extra'] = explain_row['Extra']
            context['explain_rows'] = explain_row['rows']
            context['explain_filtered'] = explain_row.get('filtered')  # can be not set
            context['explain_possible_keys'] = explain_row['possible_keys']

            reports.append(
                LinterEntry(linter_type='queries_not_using_index', table_name=table_used,
                            message='"{}" query did not make use of any index'.
                            format('{}...'.format(query[:50]) if len(query) > 50 else query),
                            context=context))

    return reports
