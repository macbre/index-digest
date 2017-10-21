from unittest import TestCase

from indexdigest.indices import Index


class TestIndex(TestCase):

    def test_repr(self):
        self.assertEqual('<Index> KEY foo (id, bar)', repr(Index(name='foo', columns=['id', 'bar'])))
        self.assertEqual('<Index> PRIMARY KEY (id)', repr(Index(name='key', columns=['id'], primary=True)))
        self.assertEqual('<Index> UNIQUE KEY idx_bar (bar)', repr(Index(name='idx_bar', columns=['bar'], unique=True)))
