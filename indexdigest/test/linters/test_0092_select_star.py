from __future__ import print_function

from unittest import TestCase

from indexdigest.linters.linter_0092_select_star import check_select_star, is_wildcard_query
from indexdigest.test import DatabaseTestMixin, read_queries_from_log


class TestLinter(TestCase, DatabaseTestMixin):

    def test_is_wildcard_query(self):
        assert is_wildcard_query('SELECT * FROM foo;')
        assert is_wildcard_query('SELECT t.* FROM foo AS t;')
        assert is_wildcard_query('SELECT  *  FROM `user`  WHERE user_id = 34994913  LIMIT 1')
        assert is_wildcard_query('/* User::loadFromDatabase */ SELECT  *  FROM `user`  WHERE user_id = 34994913  LIMIT 1')
        assert is_wildcard_query('SELECT /* User::loadFromDatabase */ *  FROM `user`  WHERE user_id = 34994913  LIMIT 1')

        assert is_wildcard_query('SELECT id FROM foo') is False
        assert is_wildcard_query('SELECT (id+2) * 2 FROM foo') is False
        assert is_wildcard_query('SELECT 3 * 3') is False
        assert is_wildcard_query('SELECT count(*) FROM foo') is False
        assert is_wildcard_query('SELECT /* foo */ test FROM foo') is False

        assert is_wildcard_query('INSERT * INTO foo') is False

        # assert False

    def test_check_select_star(self):
        reports = list(check_select_star(self.connection, read_queries_from_log('0092-select-star-log')))

        print(list(map(str, reports)))

        assert len(reports) == 2

        assert str(reports[0]) == 'foo: "SELECT * FROM foo" query uses SELECT *'
        assert reports[0].table_name == 'foo'
        assert reports[0].context['query'] == 'SELECT * FROM foo;'

        assert str(reports[1]) == 'bar: "SELECT t.* FROM bar AS t" query uses SELECT *'
        assert reports[1].table_name == 'bar'
        assert reports[1].context['query'] == 'SELECT t.* FROM bar AS t;'

        # assert False
