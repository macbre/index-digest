"""
Contains linters used to check the database for improvements.
"""


class LinterEntry(object):
    """
    Wraps a single linter entry. Various formatters may display this data differently.
    """
    def __init__(self, linter_type, table_name, message, context=None):
        """
        :type linter_type str
        :type table_name str
        :type message str
        :type context dict
        """
        self.linter_type = linter_type
        self.table_name = table_name
        self.message = message
        self.context = context

    def __str__(self):
        return '{table_name}: {message}'.format(
            table_name=self.table_name, message=self.message)

    def is_of_type(self, type_to_check):
        """
        :type type_to_check str
        :rtype: bool
        """
        return self.linter_type == type_to_check

    def get_context(self):
        """
        :rtype: dict
        """
        return self.context
