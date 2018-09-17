from unittest import TestCase

from indexdigest import VERSION
from indexdigest.formatters.syslog import format_report
from . import FormatterTestMixin

from indexdigest.cli.script import get_reports


class TestFormatter(TestCase, FormatterTestMixin):

    def test_format_report_helper(self):
        report = next(self.get_reports_mock())
        out = format_report(self.get_database_mock(), report)
        print(out, report)

        self.assertEqual(
            '{"appname": "index-digest", "meta": {"version": "index-digest v' + VERSION + '", "database_name": "test_database", '
            '"database_host": "test.local", "database_version": "MySQL v1.2.3-test"}, '
            '"report": {"type": "foo_linter", "table": "table_001", "message": "Something is fishy here", '
            '"context": {"foo": 42, "test": "bar"}}}',
            out
        )

        # assert False


class TestFormatterIntegrationTest(TestCase, FormatterTestMixin):

    def test_format_for_real_reports(self):
        database = self.get_database()

        # pass all reports via syslog formatter
        for report in get_reports(database, analyze_data=True):
            try:
                format_report(database, report)
            except Exception:
                self.fail('Failed to format the following report {}'.format(str(report)))
