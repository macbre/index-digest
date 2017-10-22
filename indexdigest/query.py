"""
This module provides SQL query parsing functions
"""
import sqlparse

from sqlparse.sql import TokenList
from sqlparse.tokens import Name, Whitespace


def get_query_tokens(query):
    """
    :type query str
    :rtype: list[sqlparse.sql.Token]
    """
    tokens = TokenList(sqlparse.parse(query)[0].tokens).flatten()

    return filter(
        lambda token: token.ttype is not Whitespace,
        tokens
    )


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

        last_token = token.value.upper()

    return columns
