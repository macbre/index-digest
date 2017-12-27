from unittest import TestCase

from indexdigest.formatters import format_plain
from . import FormatterTestMixin


class TestPlainFormatter(TestCase, FormatterTestMixin):

    def test_format_plain(self):
        out = format_plain(self.get_database_mock(), self.get_reports_mock())
        print(out)

        assert 'Found 2 issue(s) to report for "test_database" database' in out
        assert 'MySQL v1.2.3-test at test.local' in out

        assert 'Something is fishy here' in out
        assert 'An index is missing' in out

    def test_format_plain_no_results(self):
        out = format_plain(self.get_database_mock(), [])
        assert out.endswith('Jolly, good! No issues to report\n')
