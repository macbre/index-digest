from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0093_having_clause import query_has_having_clause, check_having_clause
from indexdigest.test import DatabaseTestMixin, read_queries_from_log


class TestLinter(TestCase, DatabaseTestMixin):

    def test_query_has_having_clause(self):
        assert query_has_having_clause('SELECT * FROM foo having bar = 2')
        assert query_has_having_clause('SELECT * FROM foo HAVING bar = 2')

        assert query_has_having_clause("SELECT * FROM 0019_queries_not_using_indices "
                                       "WHERE foo = 'foo' HAVING bar = 'test'")
        assert query_has_having_clause("SELECT s.cust_id,count(s.cust_id) FROM SH.sales s "
                                       "GROUP BY s.cust_id HAVING s.cust_id != '1660' AND s.cust_id != '2'")

        assert query_has_having_clause('SELECT * FROM foo') is False
        assert query_has_having_clause('SELECT * FROM foo_having LIMIT 10') is False
        assert query_has_having_clause('SELECT /* having */ id FROM foo') is False

        assert query_has_having_clause('INSERT 42 INTO having') is False

    def test_having_clause(self):
        reports = list(check_having_clause(self.connection, read_queries_from_log('0093-having-clause-log')))

        print(list(map(str, reports)))

        assert len(reports) == 3

        assert str(reports[0]) == 'foo: "SELECT * FROM foo HAVING bar = 2" query uses HAVING clause'
        assert reports[0].table_name == 'foo'
        assert reports[0].context['query'] == 'SELECT * FROM foo HAVING bar = 2;'

        assert str(reports[1]) == 'SH.sales: "SELECT s.cust_id,count(s.cust_id) ' \
                                  'FROM SH.sales s ..." query uses HAVING clause'
        assert reports[1].table_name == 'SH.sales'

        assert str(reports[2]) == '0019_queries_not_using_indices: "SELECT * FROM ' \
                                  '`0019_queries_not_using_indices` WHE..." query uses HAVING clause'
        assert reports[2].table_name == '0019_queries_not_using_indices'

        # assert False
