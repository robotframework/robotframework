import unittest

from robot.utils.asserts import assert_equal, assert_true
from robot.result.tags import *


class TestTags(unittest.TestCase):

    def test_empty_init(self):
        assert_equal(list(Tags()), [])

    def test_init_with_string(self):
        assert_equal(list(Tags('string')), ['string'])

    def test_init_with_iterable_and_normalization_and_sorting(self):
        for inp in [['T 1', 't2', 't_3'],
                    ('t2', 'T 1', 't_3'),
                    ('t2', 'T 2', '__T__2__', 'T 1', 't1', 't_1', 't_3', 't3'),
                    ('', 'T 1', '', 't2', 't_3', 'NONE')]:
            assert_equal(list(Tags(inp)), ['T 1', 't2', 't_3'])

    def test_add_string(self):
        tags = Tags(['Y'])
        tags.add('x')
        assert_equal(list(tags), ['x', 'Y'])

    def test_add_iterable(self):
        tags = Tags(['A'])
        tags.add(('b b', '', 'a', 'NONE'))
        tags.add(Tags(['BB', 'C']))
        assert_equal(list(tags), ['A', 'b b', 'C'])

    def test_remove_string(self):
        tags = Tags(['a', 'B B'])
        tags.remove('a')
        assert_equal(list(tags), ['B B'])
        tags.remove('bb')
        assert_equal(list(tags), [])

    def test_remove_non_existing(self):
        tags = Tags(['a'])
        tags.remove('nonex')
        assert_equal(list(tags), ['a'])

    def test_remove_iterable(self):
        tags = Tags(['a', 'B B'])
        tags.remove(['nonex', '', 'A'])
        tags.remove(Tags('__B_B__'))
        assert_equal(list(tags), [])

    def test_remove_using_pattern(self):
        tags = Tags(['t1', 't2', '1', '1more'])
        tags.remove('?2')
        assert_equal(list(tags), ['1', '1more', 't1'])
        tags.remove('*1*')
        assert_equal(list(tags), [])

    def test_add_and_remove_none(self):
        tags = Tags(['t'])
        tags.add(None)
        tags.remove(None)
        assert_equal(list(tags), ['t'])

    def test_contains(self):
        assert_true('a' in Tags(['a', 'b']))
        assert_true('c' not in Tags(['a', 'b']))
        assert_true('AA' in Tags(['a_a', 'b']))

    def test_contains_pattern(self):
        assert_true('a*' in Tags(['a', 'b']))
        assert_true('a*' in Tags(['u2', 'abba']))
        assert_true('a?' not in Tags(['a', 'abba']))

    def test_length(self):
        assert_equal(len(Tags()), 0)
        assert_equal(len(Tags(['a', 'b'])), 2)

    def test_truth(self):
        assert_true(not Tags())
        assert_true(Tags(['a']))

    def test_unicode(self):
        assert_equal(unicode(Tags()), '[]')
        assert_equal(unicode(Tags(['y', "X'X"])), "[X'X, y]")
        assert_equal(unicode(Tags([u'\xe4', 'a'])), u'[a, \xe4]')

    def test_str(self):
        assert_equal(str(Tags()), '[]')
        assert_equal(str(Tags(['y', "X'X"])), "[X'X, y]")
        assert_equal(str(Tags([u'\xe4', 'a'])), '[a, \xc3\xa4]')


if __name__ == '__main__':
    unittest.main()
