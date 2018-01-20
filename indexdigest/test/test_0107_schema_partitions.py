from __future__ import print_function

from unittest import TestCase

from indexdigest.test import DatabaseTestMixin


class TestSchemaWithPartition(TestCase, DatabaseTestMixin):

    def test_schema_partitions(self):
        schema = self.connection.get_table_schema('0107_schema_partitions')
        print(schema)

        assert '/*!50100' not in schema
