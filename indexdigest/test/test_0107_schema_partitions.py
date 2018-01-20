from __future__ import print_function

from unittest import TestCase

from indexdigest.test import DatabaseTestMixin


class TestSchemaWithPartition(TestCase, DatabaseTestMixin):

    def test_schema_partitions(self):
        schema = self.connection.get_table_schema('0107_schema_partitions')
        print(schema)

        assert schema == """
CREATE TABLE `0107_schema_partitions` (
  `firstname` varchar(25) NOT NULL,
  `lastname` varchar(25) NOT NULL,
  `username` varchar(16) NOT NULL,
  `email` varchar(35) DEFAULT NULL,
  `joined` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
        """.strip()
