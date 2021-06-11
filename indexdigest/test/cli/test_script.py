from _pytest.monkeypatch import MonkeyPatch
from indexdigest import VERSION
from indexdigest.cli.script import get_version


def test_get_version(monkeypatch: MonkeyPatch):
    monkeypatch.setenv('COMMIT_SHA', '1234567890abc')
    assert get_version() == f'{VERSION} (git 1234567)'
