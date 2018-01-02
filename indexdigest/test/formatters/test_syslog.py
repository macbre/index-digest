from unittest import TestCase

from indexdigest import VERSION
from indexdigest.formatters.syslog import format_report
from . import FormatterTestMixin


class TestFormatter(TestCase, FormatterTestMixin):

    def test_format_report_helper(self):
        report = next(self.get_reports_mock())
        out = format_report(self.get_database_mock(), report)
        print(out, report)

        self.assertEquals(
            '{"appname": "index-digest", "meta": {"version": "index-digest v' + VERSION + '", "database_name": "test_database", '
            '"database_host": "test.local", "database_version": "MySQL v1.2.3-test"}, '
            '"report": {"type": "foo_linter", "table": "table_001", "message": "Something is fishy here", '
            '"context": {"foo": 42, "test": "bar"}}}',
            out
        )

        # assert False
