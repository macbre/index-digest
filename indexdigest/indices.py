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

    def is_covered_by(self, index):
        """
        Checks if a current index is covered by a different one

        Examples:

        PRIMARY KEY (`id`,`foo`),
        UNIQUE KEY `idx` (`id`,`foo`)  # redundant

        PRIMARY KEY (`id`),
        KEY `idx_foo` (`foo`),  # redundant (covered by idx_foo_bar)
        KEY `idx_foo_bar` (`foo`, `bar`),
        KEY `idx_id_foo` (`id`, `foo`)

        :type index Index
        :rtype: bool
        """
        # @see https://github.com/macbre/index-digest/issues/4

        # assume primary is never covered by other indices (plus self check)
        if self.is_primary or self == index:
            return False

        # now take the subset of columns from the index we're comparing ourselves too
        columns_cnt = len(self.columns)

        if self.columns == index.columns[:columns_cnt]:
            return True

        return False

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
        return '<{}> {}'.format(self.__class__.__name__, str(self))

    def __str__(self):
        """
        :rtype: str
        """
        return '{type}{name} ({columns})'.format(
            type='PRIMARY KEY' if self.is_primary else 'UNIQUE KEY ' if self.is_unique else 'KEY ',
            name=self.name if not self.is_primary else '',
            columns=', '.join(self.columns)
        )
