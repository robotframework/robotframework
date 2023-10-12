import unittest

from robot.utils.asserts import (assert_equal, assert_false, assert_not_equal,
                                 assert_true, assert_raises)
from robot.utils import seq2str
from robot.model.tags import Tags, TagPattern, TagPatterns


class TestTags(unittest.TestCase):

    def test_empty_init(self):
        assert_equal(list(Tags()), [])

    def test_init_with_string(self):
        assert_equal(list(Tags('string')), ['string'])

    def test_init_with_iterable_and_normalization_and_sorting(self):
        for inp in [['T 1', 't2', 't_3'],
                    ('t2', 'T 1', 't_3'),
                    ('t2', 'T 1', 't_3') + ('t2', 'T 1', 't_3'),
                    ('t2', 'T 2', '__T__2__', 'T 1', 't1', 't_1', 't_3', 't3'),
                    ('', 'T 1', '', 't2', 't_3', 'NONE', 'None')]:
            assert_equal(list(Tags(inp)), ['T 1', 't2', 't_3'])

    def test_init_with_non_strings(self):
        assert_equal(list(Tags([2, True, None])), ['2', 'True'])

    def test_init_with_none(self):
        assert_equal(list(Tags(None)), [])

    def test_robot(self):
        assert_equal(Tags().robot('x'), False)
        assert_equal(Tags('robot:x').robot('x'), True)
        assert_equal(Tags(['ROBOT : X']).robot('x'), True)
        assert_equal(Tags('robot:x:y').robot('x:y'), True)
        assert_equal(Tags('robot:x').robot('y'), False)

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
        assert_true(not Tags('NONE'))
        assert_true(Tags(['a']))

    def test_str(self):
        assert_equal(str(Tags()), '[]')
        assert_equal(str(Tags(['y', "X'X", 'Y'])), "[X'X, y]")
        assert_equal(str(Tags(['ä', 'a'])), '[a, ä]')

    def test_repr(self):
        for tags in ([], ['y', "X'X"], ['ä', 'a']):
            assert_equal(repr(Tags(tags)), repr(sorted(tags)))

    def test__add__list(self):
        tags = Tags(['xx', 'yy'])
        new_tags = tags + ['zz', 'ee', 'XX']
        assert_true(isinstance(new_tags, Tags))
        assert_equal(list(tags), ['xx', 'yy'])
        assert_equal(list(new_tags), ['ee', 'xx', 'yy', 'zz'])

    def test__add__tags(self):
        tags1 = Tags(['xx', 'yy'])
        tags2 = Tags(['zz', 'ee', 'XX'])
        new_tags = tags1 + tags2
        assert_true(isinstance(new_tags, Tags))
        assert_equal(list(tags1), ['xx', 'yy'])
        assert_equal(list(tags2), ['ee', 'XX', 'zz'])
        assert_equal(list(new_tags), ['ee', 'xx', 'yy', 'zz'])

    def test__add__None(self):
        tags = Tags(['xx', 'yy'])
        new_tags = tags + None
        assert_true(isinstance(new_tags, Tags))
        assert_equal(list(tags), ['xx', 'yy'])
        assert_equal(list(new_tags), list(tags))
        assert_true(new_tags is not tags)

    def test_getitem_with_index(self):
        tags = Tags(['2', '0', '1'])
        assert_equal(tags[0], '0')
        assert_equal(tags[1], '1')
        assert_equal(tags[2], '2')

    def test_getitem_with_slice(self):
        tags = Tags(['2', '0', '1'])
        self._verify_slice(tags[:], ['0', '1', '2'])
        self._verify_slice(tags[1:], ['1', '2'])
        self._verify_slice(tags[1:-1], ['1'])
        self._verify_slice(tags[1:-2], [])
        self._verify_slice(tags[::2], ['0', '2'])

    def _verify_slice(self, sliced, expected):
        assert_true(isinstance(sliced, Tags))
        assert_equal(list(sliced), expected)

    def test__eq__(self):
        assert_equal(Tags(['x']), Tags(['x']))
        assert_equal(Tags(['X']), Tags(['x']))
        assert_equal(Tags(['X', 'YZ']), Tags(('x', 'y_z')))
        assert_not_equal(Tags(['X']), Tags(['Y']))

    def test__eq__converts_other_to_tags(self):
        assert_equal(Tags(['X']), ['x'])
        assert_equal(Tags(['X']), 'x')
        assert_not_equal(Tags(['X']), 'y')

    def test__eq__with_other_that_cannot_be_converted_to_tags(self):
        assert_not_equal(Tags(), 1)
        assert_not_equal(Tags(), None)

    def test__eq__normalized(self):
        assert_equal(Tags(['Hello world', 'Foo', 'Not_world']),
                     Tags(['nOT WORLD', 'FOO', 'hello world']))

    def test__slots__(self):
        assert_raises(AttributeError, setattr, Tags(), 'attribute', 'value')


class TestNormalizing(unittest.TestCase):

    def test_empty(self):
        self._verify([], [])

    def test_case_and_space(self):
        for inp in ['lower'], ['MiXeD', 'UPPER'], ['a few', 'spaces here']:
            self._verify(inp, inp)

    def test_underscore(self):
        self._verify(['a_tag', 'a tag', 'ATag'], ['a_tag'])
        self._verify(['tag', '_t_a_g_'], ['tag'])

    def test_remove_empty_and_none(self):
        for inp in ['', 'X', '', '  ', '\n'], ['none', 'N O N E', 'X', '', '_']:
            self._verify(inp, ['X'])

    def test_remove_dupes(self):
        for inp in ['dupe', 'DUPE', ' d u p e '], ['d U', 'du', 'DU', 'Du']:
            self._verify(inp, [inp[0]])

    def test_sorting(self):
        for inp, exp in [(['SORT', '1', 'B', '2', 'a'],
                          ['1', '2', 'a', 'B', 'SORT']),
                         (['all', 'A LL', 'NONE', '10', '1', 'A', 'a', '', 'b'],
                          ['1', '10', 'A', 'all', 'b'])]:
            self._verify(inp, exp)

    def _verify(self, tags, expected):
        assert_equal(list(Tags(tags)), expected)


class TestTagPatterns(unittest.TestCase):

    def test_single_pattern(self):
        patterns = TagPatterns(['x', 'y', 'z*'])
        assert_false(patterns.match([]))
        assert_false(patterns.match(['no', 'match']))
        assert_true(patterns.match(['x']))
        assert_true(patterns.match(['xxx', 'zzz']))

    def test_and(self):
        patterns = TagPatterns(['xANDy', '???ANDz'])
        assert_false(patterns.match([]))
        assert_false(patterns.match(['x']))
        assert_true(patterns.match(['x', 'y', 'z']))
        assert_true(patterns.match(['123', 'y', 'z']))

    def test_multiple_ands(self):
        patterns = TagPatterns(['xANDyANDz'])
        assert_false(patterns.match([]))
        assert_false(patterns.match(['x']))
        assert_false(patterns.match(['x', 'y']))
        assert_true(patterns.match(['x', 'Y', 'z']))
        assert_true(patterns.match(['a', 'y', 'z', 'b', 'X']))

    def test_or(self):
        patterns = TagPatterns(['xORy', '???ORz'])
        assert_false(patterns.match([]))
        assert_false(patterns.match(['a', 'b', '12', '1234']))
        assert_true(patterns.match(['x']))
        assert_true(patterns.match(['Y']))
        assert_true(patterns.match(['123']))
        assert_true(patterns.match(['Z']))
        assert_true(patterns.match(['x', 'y', 'z']))
        assert_true(patterns.match(['123', 'a', 'b', 'c', 'd']))
        assert_true(patterns.match(['a', 'b', 'c', 'd', 'Z']))

    def test_multiple_ors(self):
        patterns = TagPatterns(['xORyORz'])
        assert_false(patterns.match([]))
        assert_false(patterns.match(['xxx']))
        assert_true(all(patterns.match([c]) for c in 'XYZ'))
        assert_true(all(patterns.match(['a', 'b', c, 'd']) for c in 'xyz'))
        assert_true(patterns.match(['x', 'y']))
        assert_true(patterns.match(['x', 'Y', 'z']))

    def test_ands_and_ors(self):
        for pattern in AndOrPatternGenerator(max_length=5):
            expected = eval(pattern.lower())
            assert_equal(TagPattern.from_string(pattern).match('1'), expected)

    def test_not(self):
        patterns = TagPatterns(['xNOTy', '???NOT?'])
        assert_false(patterns.match([]))
        assert_false(patterns.match(['x', 'y']))
        assert_false(patterns.match(['123', 'y', 'z']))
        assert_true(patterns.match(['x']))
        assert_true(patterns.match(['123', 'xx']))

    def test_not_and_and(self):
        patterns = TagPatterns(['xNOTyANDz', 'aANDbNOTc',
                                '1 AND 2? AND 3?? NOT 4* AND 5* AND 6*'])
        assert_false(patterns.match([]))
        assert_false(patterns.match(['x', 'y', 'z']))
        assert_true(patterns.match(['x', 'y']))
        assert_true(patterns.match(['x']))
        assert_false(patterns.match(['a', 'b', 'c']))
        assert_false(patterns.match(['a']))
        assert_false(patterns.match(['b']))
        assert_true(patterns.match(['a', 'b']))
        assert_true(patterns.match(['a', 'b', 'xxxx']))
        assert_false(patterns.match(['1', '22', '33']))
        assert_false(patterns.match(['1', '22', '333', '4', '5', '6']))
        assert_true(patterns.match(['1', '22', '333']))
        assert_true(patterns.match(['1', '22', '333', '4', '5', '7']))

    def test_not_and_or(self):
        patterns = TagPatterns(['xNOTyORz', 'aORbNOTc',
                                '1 OR 2? OR 3?? NOT 4* OR 5* OR 6*'])
        assert_false(patterns.match([]))
        assert_false(patterns.match(['x', 'y', 'z']))
        assert_false(patterns.match(['x', 'y']))
        assert_false(patterns.match(['Z', 'x']))
        assert_true(patterns.match(['x']))
        assert_true(patterns.match(['xxx', 'X']))
        assert_true(patterns.match(['a', 'b']))
        assert_false(patterns.match(['a', 'b', 'c']))
        assert_true(patterns.match(['a']))
        assert_true(patterns.match(['B', 'XXX']))
        assert_false(patterns.match(['b', 'c']))
        assert_false(patterns.match(['c']))
        assert_true(patterns.match(['x', 'y', '321']))
        assert_false(patterns.match(['x', 'y', '32']))
        assert_false(patterns.match(['1', '2', '3', '4']))
        assert_true(patterns.match(['1', '22', '333']))

    def test_multiple_nots(self):
        patterns = TagPatterns(['xNOTyNOTz', '1 NOT 2 NOT 3 NOT 4'])
        assert_true(patterns.match(['x']))
        assert_false(patterns.match(['x', 'y']))
        assert_false(patterns.match(['x', 'z']))
        assert_false(patterns.match(['x', 'y', 'z']))
        assert_false(patterns.match(['xxx']))
        assert_true(patterns.match(['1']))
        assert_false(patterns.match(['1', '3', '4']))
        assert_false(patterns.match(['1', '2', '3']))
        assert_false(patterns.match(['1', '2', '3', '4']))

    def test_multiple_nots_with_ands(self):
        patterns = TagPatterns('a AND b NOT c AND d NOT e AND f')
        assert_true(patterns.match(['a', 'b']))
        assert_true(patterns.match(['a', 'b', 'c']))
        assert_true(patterns.match(['a', 'b', 'c', 'e']))
        assert_false(patterns.match(['a', 'b', 'c', 'd']))
        assert_false(patterns.match(['a', 'b', 'e', 'f']))
        assert_false(patterns.match(['a', 'b', 'c', 'd', 'e', 'f']))
        assert_false(patterns.match(['a', 'b', 'c', 'd', 'e']))

    def test_multiple_nots_with_ors(self):
        patterns = TagPatterns('a OR b NOT c OR d NOT e OR f')
        assert_true(patterns.match(['a']))
        assert_true(patterns.match(['B']))
        assert_false(patterns.match(['c']))
        assert_true(all(not patterns.match(['a', 'b', c]) for c in 'cdef'))
        assert_true(patterns.match(['a', 'x']))

    def test_starts_with_not(self):
        patterns = TagPatterns('NOTe')
        assert_true(patterns.match('d'))
        assert_false(patterns.match('e'))
        patterns = TagPatterns('NOT e OR f')
        assert_true(patterns.match('d'))
        assert_false(patterns.match('e'))
        assert_false(patterns.match('f'))

    def test_str(self):
        for pattern in ['a', 'NOT a', 'a NOT b', 'a AND b', 'a OR b', 'a*',
                        'a OR b NOT c OR d AND e OR ??']:
            assert_equal(str(TagPatterns(pattern)),
                         f'[{pattern}]')
            assert_equal(str(TagPatterns(pattern.replace(' ', ''))),
                         f'[{pattern}]')
            assert_equal(str(TagPatterns([pattern, 'x', pattern, 'y'])),
                         f'[{pattern}, x, y]')

    def test_non_ascii(self):
        pattern = 'ä OR å NOT æ AND ☃ OR ??'
        expected = f'[{pattern}]'
        assert_equal(str(TagPatterns(pattern)), expected)
        assert_equal(str(TagPatterns(pattern.replace(' ', ''))), expected)

    def test_seq2str(self):
        patterns = TagPatterns(['isä', 'äiti'])
        assert_equal(seq2str(patterns), "'isä' and 'äiti'")


class AndOrPatternGenerator:
    tags = ['0', '1']
    operators = ['OR', 'AND']

    def __init__(self, max_length):
        self.max_length = max_length

    def __iter__(self):
        for tag in self.tags:
            for pattern in self._generate([tag], self.max_length-1):
                yield pattern

    def _generate(self, tokens, length):
        yield ' '.join(tokens)
        if length:
            for operator in self.operators:
                for tag in self.tags:
                    for pattern in self._generate(tokens + [operator, tag],
                                                  length-1):
                        yield pattern


if __name__ == '__main__':
    unittest.main()
