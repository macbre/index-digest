"""
Data structures and utilities for handling table indices
"""


class Index(object):
    """
    Keeps a single index meta-data
    """
    def __init__(self, name, columns, unique=False, primary=False):
        """
        :type name str
        :type columns list[str]
        :type unique bool
        :type primary bool
        """
        self._name = name
        self._columns = columns
        self._unique = unique
        self._primary = primary

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @property
    def columns(self):
        """
        :rtype: list[str]
        """
        return self._columns

    @property
    def is_unique(self):
        """
        :rtype: bool
        """
        return self._unique is True

    @property
    def is_primary(self):
        """
        :rtype: bool
        """
        return self._primary is True

    def __repr__(self):
        """
        :rtype: str
        """
        return '<{_}> {type}{name} ({columns})'.format(
            _=self.__class__.__name__,
            type='PRIMARY KEY' if self.is_primary else 'UNIQUE KEY ' if self.is_unique else 'KEY ',
            name=self.name if not self.is_primary else '',
            columns=', '.join(self.columns)
        )
