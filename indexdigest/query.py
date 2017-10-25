"""
This module provides SQL query parsing functions
"""
import sqlparse

from sqlparse.sql import TokenList
from sqlparse.tokens import Name, Whitespace, Wildcard


def get_query_tokens(query):
    """
    :type query str
    :rtype: list[sqlparse.sql.Token]
    """
    tokens = TokenList(sqlparse.parse(query)[0].tokens).flatten()
    # print([(token.value, token.ttype) for token in tokens])

    return [token for token in tokens if token.ttype is not Whitespace]


def get_query_columns(query):
    """
    :type query str
    :rtype: list[str]
    """
    columns = []
    last_keyword = None
    last_token = None

    for token in get_query_tokens(query):
        if token.is_keyword and token.value.upper() not in ['AS', 'AND', 'OR']:
            # keep the name of the last keyword, e.g. SELECT, FROM, WHERE, (ORDER) BY
            last_keyword = token.value.upper()
            # print('keyword', last_keyword)
        elif token.ttype is Name:
            # analyze the name tokens, column names and where condition values
            if last_keyword in ['SELECT', 'WHERE', 'BY'] and last_token not in ['AS']:
                # print(last_keyword, last_token, token.value)

                if token.value not in columns:
                    columns.append(token.value)
        elif token.ttype is Wildcard:
            # handle wildcard in SELECT part, but ignore count(*)
            # print(last_keyword, last_token, token.value)
            if last_keyword == 'SELECT' and last_token != '(':
                columns.append(token.value)

        last_token = token.value.upper()

    return columns


def get_query_tables(query):
    """
    :type query str
    :rtype: list[str]
    """
    tables = []
    last_keyword = None
    last_token = None

    table_syntax_keywords = ['FROM', 'WHERE', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'ON']

    for token in get_query_tokens(query):
        # print([token, token.ttype])
        if token.is_keyword and token.value.upper() in table_syntax_keywords:
            # keep the name of the last keyword
            last_keyword = token.value.upper()
            # print('keyword', last_keyword)
        elif token.ttype is Name or token.is_keyword:
            # print([last_keyword, last_token, token.value])
            # analyze the name tokens, column names and where condition values
            if last_keyword in ['FROM', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN'] \
                    and last_token not in ['AS']:
                if token.value not in tables:
                    tables.append(token.value.strip('`'))

        last_token = token.value.upper()

    return tables
