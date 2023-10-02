import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Union

from robot.errors import DataError
from robot.running.arguments.typeinfo import TypeInfo, TypeInfoParser
from robot.utils.asserts import assert_equal, assert_raises_with_msg


class TestTypeInfo(unittest.TestCase):

    def test_ellipsis_conversion(self):
        assert_equal(TypeInfo('...').type, Ellipsis)
        assert_equal(TypeInfo('...').name, '...')

    def test_type_from_name(self):
        for name, expected in [('...', Ellipsis),
                               ('any', Any),
                               ('str', str),
                               ('string', str),
                               ('unicode', str),
                               ('boolean', bool),
                               ('bool', bool),
                               ('int', int),
                               ('integer', int),
                               ('long', int),
                               ('float', float),
                               ('double', float),
                               ('decimal', Decimal),
                               ('bytes', bytes),
                               ('bytearray', bytearray),
                               ('datetime', datetime),
                               ('date', date),
                               ('timedelta', timedelta),
                               ('path', Path),
                               ('none', type(None)),
                               ('list', list),
                               ('sequence', list),
                               ('tuple', tuple),
                               ('dictionary', dict),
                               ('dict', dict),
                               ('map', dict),
                               ('mapping', dict),
                               ('set', set),
                               ('frozenset', frozenset),
                               ('union', Union)]:
            for name in name, name.upper():
                assert_equal(TypeInfo(name).type, expected)
                assert_equal(TypeInfo(name).name, name)

    def test_union(self):
        for union in [Union[int, str, float],
                      (int, str, float),
                      [int, str, float],
                      Union[int, Union[str, float]],
                      (int, [str, float])]:
            info = TypeInfo.from_type_hint(union)
            assert_equal(info.name, 'Union')
            assert_equal(info.is_union, True)
            assert_equal(info.nested[0].type, int)
            assert_equal(info.nested[0].name, 'int')
            assert_equal(info.nested[1].type, str)
            assert_equal(info.nested[1].name, 'str')
            assert_equal(info.nested[2].type, float)
            assert_equal(info.nested[2].name, 'float')
            assert_equal(len(info.nested), 3)

    def test_union_with_one_type_is_reduced_to_the_type(self):
        for union in Union[int], (int,):
            info = TypeInfo.from_type_hint(union)
            assert_equal(info.type, int)
            assert_equal(info.name, 'int')
            assert_equal(info.is_union, False)
            assert_equal(len(info.nested), 0)

    def test_empty_union_not_allowed(self):
        for union in Union, ():
            assert_raises_with_msg(DataError, 'Union used as a type hint cannot be empty.',
                                   TypeInfo.from_type_hint, union)

    def test_non_type(self):
        for item in 42, object(), set(), b'hello':
            info = TypeInfo.from_type_hint(item)
            assert_equal(info.name, str(item))
            assert_equal(info.type, None)


class TestTypeInfoParser(unittest.TestCase):

    def test_simple(self):
        for name in 'str', 'Integer', 'whatever', 'two parts', 'non-alpha!?':
            info = TypeInfoParser(name).parse()
            assert_equal(info.name, name)

    def test_parameterized(self):
        info = TypeInfoParser('list[int]').parse()
        assert_equal(info.name, 'list')
        assert_equal(info.nested[0].name, 'int')

    def test_multiple_parameters(self):
        info = TypeInfoParser('Mapping[str, int]').parse()
        assert_equal(info.name, 'Mapping')
        assert_equal(info.nested[0].name, 'str')
        assert_equal(info.nested[1].name, 'int')

    def test_union(self):
        info = TypeInfoParser('int | float').parse()
        assert_equal(info.name, 'Union')
        assert_equal(info.nested[0].name, 'int')
        assert_equal(info.nested[1].name, 'float')

    def test_union_with_multiple_types(self):
        types = list('abcdefg')
        info = TypeInfoParser('|'.join(types)).parse()
        assert_equal(info.name, 'Union')
        assert_equal(len(info.nested), len(types))
        for nested, name in zip(info.nested, types):
            assert_equal(nested.name, name)

    def test_mixed(self):
        info = TypeInfoParser('int | list[int] |tuple[int,int|tuple[int, int|str]]').parse()
        assert_equal(info.name, 'Union')
        assert_equal(info.nested[0].name, 'int')
        assert_equal(info.nested[1].name, 'list')
        assert_equal(info.nested[1].nested[0].name, 'int')
        assert_equal(info.nested[2].name, 'tuple')
        assert_equal(info.nested[2].nested[0].name, 'int')
        assert_equal(info.nested[2].nested[1].name, 'Union')
        assert_equal(info.nested[2].nested[1].nested[0].name, 'int')
        assert_equal(info.nested[2].nested[1].nested[1].name, 'tuple')
        assert_equal(info.nested[2].nested[1].nested[1].nested[0].name, 'int')
        assert_equal(info.nested[2].nested[1].nested[1].nested[1].name, 'Union')
        assert_equal(info.nested[2].nested[1].nested[1].nested[1].nested[0].name, 'int')
        assert_equal(info.nested[2].nested[1].nested[1].nested[1].nested[1].name, 'str')

    def test_errors(self):
        for info, position, error in [
                ('',       'end', 'Type name missing.'),
                ('[',      0,     'Type name missing.'),
                (']',      0,     'Type name missing.'),
                (',',      0,     'Type name missing.'),
                ('|',      0,     'Type name missing.'),
                ('x[',     'end', 'Type name missing.'),
                ('x]',     1,     "Extra content after 'x'."),
                ('x,',     1,     "Extra content after 'x'."),
                ('x|',     'end', 'Type name missing.'),
                ('x[y][',  4,     "Extra content after 'x[y]'."),
                ('x[y]]',  4,     "Extra content after 'x[y]'."),
                ('x[y],',  4,     "Extra content after 'x[y]'."),
                ('x[y]|',  'end', 'Type name missing.'),
                ('x[y]z',  4,     "Extra content after 'x[y]'."),
                ('x[y',    'end', "Closing ']' missing."),
                ('x[y,',   'end', 'Type name missing.'),
                ('x[y,z',  'end', "Closing ']' missing."),
                ('x[,',    2,     'Type name missing.'),
                ('x[[y]]', 2,     'Type name missing.'),
                ('x | ,',  4,     'Type name missing.'),
                ('x|||',   2,     'Type name missing.'),
        ]:
            position = f'index {position}' if isinstance(position, int) else position
            assert_raises_with_msg(
                ValueError,
                f"Parsing type '{info}' failed: Error at {position}: {error}",
                TypeInfoParser(info).parse
            )


if __name__ == '__main__':
    unittest.main()
