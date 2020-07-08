from unittest import TestCase

from indexdigest.schema import Column


class TestColumn(TestCase):

    def test_is_text_type(self):
        text_types = [
            'CHAR(16)',
            'VARCHAR(16)',
            'CHAR(32)',
            'VARCHAR(32)',
            'BINARY(16)',
            'VARBINARY(16)',
            'BINARY(32)',
            'VARBINARY(32)',
            'TEXT',
            'BLOB',
            "SET('a', 'b', 'c', 'd')",
            "ENUM('x-small', 'small', 'medium', 'large', 'x-large')",
        ]

        not_text_types = [
            'INT',
            'BIGINT',
            'INT(9)',
            'TIMESTAMP',
            'DATETIME',
        ]

        for text_type in text_types:
            self.assertTrue(
                expr=Column('foo', column_type=text_type, character_set='utf8').is_text_type(),
                msg=text_type)

        for not_text_type in not_text_types:
            self.assertFalse(
                expr=Column('foo', column_type=not_text_type, character_set='utf8').is_text_type(),
                msg=not_text_type)

    def test_is_timestamp_type(self):
        timestamp_types = [
            'TIMESTAMP',
            'DATETIME',
            'DATE',
            'TIME',
            'YEAR',
        ]

        not_timestamp_types = [
            'INT',
            'BIGINT',
            'INT(9)',
            'CHAR(16)',
            'VARCHAR(16)',
            'CHAR(32)',
            'VARCHAR(32)',
            'BINARY(16)',
            'VARBINARY(16)',
            'BINARY(32)',
            'VARBINARY(32)',
            'TEXT',
            'BLOB',
            "SET('a', 'b', 'c', 'd')",
            "ENUM('x-small', 'small', 'medium', 'large', 'x-large')",
        ]

        for timestamp_type in timestamp_types:
            self.assertTrue(
                expr=Column('foo', column_type=timestamp_type, character_set='utf8').is_timestamp_type(),
                msg=timestamp_type)

        for not_timestamp_type in not_timestamp_types:
            self.assertFalse(
                expr=Column('foo', column_type=not_timestamp_type, character_set='utf8').is_timestamp_type(),
                msg=not_timestamp_type)
