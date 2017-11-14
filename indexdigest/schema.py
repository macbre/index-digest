"""
Data structures for handling schema-related things like indices and columns
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

        # equal indices - prefer unique over non unique indices
        # and primary keys over unique ones
        # @see https://github.com/macbre/index-digest/issues/49
        if self.columns == index.columns and self.is_unique:
            # we're covered by the same unique key or a primary key
            if index.is_unique or index.is_primary:
                return True

            return False

        # now take the subset of columns from the index we're comparing ourselves too
        columns_cnt = len(self.columns)

        if self.columns == index.columns[:columns_cnt]:
            if self.is_unique and index.is_primary:
                # the unique key adds a uniqueness bit to the primary key - #49
                return False

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


class Column(object):
    """
    Keeps a single table column meta-data

    @see https://dev.mysql.com/doc/refman/5.7/en/columns-table.html
    """
    def __init__(self, name, column_type, character_set=None, collation=None):
        """
        :type name str
        :type column_type str
        :type character_set str
        :type collation str
        """
        self._name = name
        self._type = column_type
        self._character_set = character_set
        self._collation = collation

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @property
    def type(self):
        """
        :rtype: str
        """
        return self._type

    @property
    def character_set(self):
        """
        :rtype: str
        """
        return self._character_set

    @property
    def collation(self):
        """
        :rtype: str
        """
        return self._collation

    def is_text_type(self):
        """
        :rtype: bool
        """
        base_type = self.type.split('(')[0].upper()
        # @see https://dev.mysql.com/doc/refman/5.7/en/string-types.html
        return base_type in \
               ['CHAR', 'VARCHAR', 'BINARY', 'VARBINARY', 'BLOB', 'TEXT', 'ENUM', 'SET']

    def is_timestamp_type(self):
        """
        :rtype: bool
        """
        base_type = self.type.upper()
        # @see https://dev.mysql.com/doc/refman/5.7/en/date-and-time-types.html
        return base_type in \
               ['DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'YEAR']

    def __repr__(self):
        """
        :rtype: str
        """
        return '<{}> {}'.format(self.__class__.__name__, str(self))

    def __str__(self):
        """
        :rtype: str
        """
        return self._name
