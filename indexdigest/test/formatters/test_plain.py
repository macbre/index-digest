# -*- coding: utf-8 -*-
import re

from unittest import TestCase

from indexdigest import VERSION
from indexdigest.formatters import format_plain as formatter
from . import FormatterTestMixin


class TestFormatter(TestCase, FormatterTestMixin):

    @staticmethod
    def _remove_ansi_styles(text):
        """
        :type text str
        :rtype: str
        """
        # '\033[0m'
        return re.sub(r'\033\[\d+m', '', text)

    def test_format_plain(self):
        out = formatter(self.get_database_mock(), self.get_reports_mock())
        out = self._remove_ansi_styles(out)
        print(out)

        assert 'Found 2 issue(s) to report for "test_database" database' in out
        assert 'MySQL v1.2.3-test at test.local' in out
        assert 'index-digest v' + VERSION in out

        assert 'foo_linter → table affected: table_001' in out
        assert '✗ Something is fishy here' in out
        assert '  - foo: 42\n  - test: bar' in out

        assert 'bar_linter → table affected: table_042' in out
        assert '✗ An index is missing' in out

        assert out.endswith('Queries performed: 0')
        # assert False

    def test_format_plain_no_results(self):
        out = formatter(self.get_database_mock(), [])
        assert out.endswith('Jolly, good! No issues to report')
