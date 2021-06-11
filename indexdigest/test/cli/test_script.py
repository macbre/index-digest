from unittest import TestCase

from _pytest.monkeypatch import MonkeyPatch

from indexdigest import VERSION
from indexdigest.cli.script import filter_reports_by_type, filter_reports_by_table, get_version
from indexdigest.utils import LinterEntry


class FilterReportsByTypeTest(TestCase):

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

        filtered = filter_reports_by_type(reports)
        print(filtered)

        assert len(filtered) == len(self.REPORT_TYPES)

    def test_checks_switch(self):
        reports = self.get_reports_mock(self.REPORT_TYPES)

        filtered = filter_reports_by_type(reports, checks='foo,test')
        print(filtered)

        assert len(filtered) == 3
        assert filtered[0].linter_type == 'foo'
        assert filtered[1].linter_type == 'test'
        assert filtered[2].linter_type == 'test'

    def test_checks_switch_single(self):
        reports = self.get_reports_mock(self.REPORT_TYPES)

        filtered = filter_reports_by_type(reports, checks='test')
        print(filtered)

        assert len(filtered) == 2
        assert filtered[0].linter_type == 'test'
        assert filtered[1].linter_type == 'test'

    def test_skip_checks_switch(self):
        reports = self.get_reports_mock(self.REPORT_TYPES)

        filtered = filter_reports_by_type(reports, skip_checks='foo,test')
        print(filtered)

        assert len(filtered) == 2
        assert filtered[0].linter_type == 'bar'
        assert filtered[1].linter_type == 'foobar'


class FilterReportsByTableTest(TestCase):

    REPORT_TABLES = [
        'foo',
        'bar',
        'test',
        'test',
        'foobar',
    ]

    @staticmethod
    def get_reports_mock(tables):
        """
        :type tables list[str]
        :rtype: list[LinterEntry]
        """
        return [
            LinterEntry(linter_type='foo', table_name=table, message='message')
            for table in tables
        ]

    def test_noop(self):
        reports = self.get_reports_mock(self.REPORT_TABLES)

        filtered = filter_reports_by_table(reports)
        print(filtered)

        assert len(filtered) == len(self.REPORT_TABLES)

    def test_tables_switch(self):
        reports = self.get_reports_mock(self.REPORT_TABLES)

        filtered = filter_reports_by_table(reports, tables='foo,test')
        print(filtered)

        assert len(filtered) == 3
        assert filtered[0].table_name == 'foo'
        assert filtered[1].table_name == 'test'
        assert filtered[2].table_name == 'test'

    def test_tables_switch_single(self):
        reports = self.get_reports_mock(self.REPORT_TABLES)

        filtered = filter_reports_by_table(reports, tables='test')
        print(filtered)

        assert len(filtered) == 2
        assert filtered[0].table_name == 'test'
        assert filtered[1].table_name == 'test'

    def test_skip_tables_switch(self):
        reports = self.get_reports_mock(self.REPORT_TABLES)

        filtered = filter_reports_by_table(reports, skip_tables='foo,test')
        print(filtered)

        assert len(filtered) == 2
        assert filtered[0].table_name == 'bar'
        assert filtered[1].table_name == 'foobar'


def test_get_version(monkeypatch: MonkeyPatch):
    monkeypatch.setenv('COMMIT_SHA', '1234567890abc')
    assert get_version() == f'{VERSION} (git 1234567)'
