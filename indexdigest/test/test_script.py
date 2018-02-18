from unittest import TestCase

from indexdigest.cli.script import filter_reports
from indexdigest.utils import LinterEntry


class TestFormatterIntegrationTest(TestCase):

    REPORT_TYPES = [
        'foo',
        'bar',
        'test',
        'test',
        'foobar',
    ]

    @staticmethod
    def get_reports_mock(linter_types):
        """
        :type linter_types list[str]
        :rtype: list[LinterEntry]
        """
        return [
            LinterEntry(linter_type=linter_type, table_name='foo', message='message')
            for linter_type in linter_types
        ]

    def test_noop(self):
        reports = self.get_reports_mock(self.REPORT_TYPES)

        filtered = filter_reports(reports)
        print(filtered)

        assert len(filtered) == len(self.REPORT_TYPES)

    def test_checks_switch(self):
        reports = self.get_reports_mock(self.REPORT_TYPES)

        filtered = filter_reports(reports, checks='foo,test')
        print(filtered)

        assert len(filtered) == 3
        assert filtered[0].linter_type == 'foo'
        assert filtered[1].linter_type == 'test'
        assert filtered[2].linter_type == 'test'

    def test_checks_switch_single(self):
        reports = self.get_reports_mock(self.REPORT_TYPES)

        filtered = filter_reports(reports, checks='test')
        print(filtered)

        assert len(filtered) == 2
        assert filtered[0].linter_type == 'test'
        assert filtered[1].linter_type == 'test'

    def test_skip_checks_switch(self):
        reports = self.get_reports_mock(self.REPORT_TYPES)

        filtered = filter_reports(reports, skip_checks='foo,test')
        print(filtered)

        assert len(filtered) == 2
        assert filtered[0].linter_type == 'bar'
        assert filtered[1].linter_type == 'foobar'
