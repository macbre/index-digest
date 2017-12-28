import yaml

from unittest import TestCase

from indexdigest.schema import Index
from indexdigest.utils import LinterEntry
from indexdigest.formatters import format_yaml as formatter
from . import FormatterTestMixin


class TestFormatter(TestCase, FormatterTestMixin):

    def test_formatter(self):
        out = formatter(self.get_database_mock(), self.get_reports_mock())
        print(out)

        # first check that it's a valid YAML
        res = yaml.safe_load(out)
        assert 'meta' in res
        assert 'reports' in res

        assert 'version: index-digest v0.1.0\n  database_name: test_database\n' \
            '  database_host: test.local\n  database_version: MySQL v1.2.3-test' in out

        assert 'message: Something is fishy here' in out

        # context fields order is maintained
        assert '  context:\n    foo: 42\n    test: bar\n' in out

        # properly marked YAML file
        assert out.startswith('---')
        assert out.endswith('...\n')
        # assert False

    def test_formatter_no_results(self):
        out = formatter(self.get_database_mock(), [])
        print(out)

        assert out.endswith('reports: []\n...\n')

    def test_index_representer(self):
        reports = [
            LinterEntry(
                linter_type='foo',
                table_name='foo',
                message='foo',
                context={
                    'index': Index('foo', ['bar'], primary=True)
                }
            )
        ]

        out = formatter(self.get_database_mock(), reports)
        print(out)

        assert '  context:\n    index: !index \'PRIMARY KEY (bar)\'' in out

        # assert False
