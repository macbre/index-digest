from unittest import TestCase

from indexdigest.schema import Index


class TestIndex(TestCase):

    def test_repr(self):
        self.assertEqual('<Index> KEY foo (id, bar)', repr(Index(name='foo', columns=['id', 'bar'])))
        self.assertEqual('<Index> PRIMARY KEY (id)', repr(Index(name='key', columns=['id'], primary=True)))
        self.assertEqual('<Index> UNIQUE KEY idx_bar (bar)', repr(Index(name='idx_bar', columns=['bar'], unique=True)))

    def test_is_covered_by(self):
        # #1 case
        primary = Index(name='base', columns=['id', 'bar'], primary=True)
        second = Index(name='base', columns=['id', 'bar'])

        self.assertFalse(primary.is_covered_by(second))
        self.assertTrue(second.is_covered_by(primary))

        # self-check
        self.assertFalse(second.is_covered_by(second))

        # #2 case
        first = Index(name='base', columns=['id', 'bar', 'foo'])
        second = Index(name='base', columns=['id', 'bar'])

        self.assertFalse(first.is_covered_by(second))
        self.assertTrue(second.is_covered_by(first))

        # #3 case
        first = Index(name='base', columns=['id', 'bar', 'foo'])
        second = Index(name='base', columns=['id', 'bar', 'foo'])

        self.assertTrue(first.is_covered_by(second))
        self.assertTrue(second.is_covered_by(first))

        # #4 case
        first = Index(name='base', columns=['id', 'bar', 'foo'])
        second = Index(name='base', columns=['bar', 'foo'])

        self.assertFalse(first.is_covered_by(second))
        self.assertFalse(second.is_covered_by(first))

    def test_primary_and_unique_keys_coverage(self):
        # @see https://github.com/macbre/index-digest/issues/49

        # second key adds a uniqueness constraint, keep it
        first = Index(name='base', columns=['bar', 'foo'], primary=True)
        second = Index(name='base', columns=['bar'], unique=True)

        self.assertFalse(first.is_covered_by(second))
        self.assertFalse(second.is_covered_by(first))

        # these keys are the same (primary is unique)
        first = Index(name='base', columns=['bar', 'foo'], primary=True)
        second = Index(name='base', columns=['bar', 'foo'], unique=True)

        self.assertFalse(first.is_covered_by(second))
        self.assertTrue(second.is_covered_by(first))

        # prefer unique over non-unique
        first = Index(name='base', columns=['bar', 'foo'], unique=True)
        second = Index(name='base', columns=['bar', 'foo'])

        self.assertFalse(first.is_covered_by(second))
        self.assertTrue(second.is_covered_by(first))

        # identical unique indices
        first = Index(name='base', columns=['bar', 'foo'], unique=True)
        second = Index(name='base', columns=['bar', 'foo'], unique=True)

        self.assertTrue(first.is_covered_by(second))
        self.assertTrue(second.is_covered_by(first))
