import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Generic, List, Mapping, Sequence, Set, Tuple, TypeVar, Union

from robot.errors import DataError
from robot.running.arguments.typeinfo import TypeInfo, TypeInfoParser, TYPE_NAMES
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
            assert_raises_with_msg(
                DataError, 'Union used as a type hint cannot be empty.',
                TypeInfo.from_type_hint, union
            )

    def test_valid_params(self):
        for typ in (List[int], Sequence[int], Set[int], Tuple[int], 'list[int]',
                    'SEQUENCE[INT]', 'Set[integer]', 'frozenset[int]', 'tuple[int]'):
            info = TypeInfo.from_type_hint(typ)
            assert_equal(len(info.nested), 1)
            assert_equal(info.nested[0].type, int)
        for typ in Dict[int, str], Mapping[int, str], 'dict[int, str]', 'MAP[INT,STR]':
            info = TypeInfo.from_type_hint(typ)
            assert_equal(len(info.nested), 2)
            assert_equal(info.nested[0].type, int)
            assert_equal(info.nested[1].type, str)

    def test_invalid_sequence_params(self):
        for typ in 'list[int, str]', 'SEQUENCE[x, y]', 'Set[x, y]', 'frozenset[x, y]':
            name = typ.split('[')[0]
            assert_raises_with_msg(
                DataError,
                f"'{name}[]' requires exactly 1 argument, '{typ}' has 2.",
                TypeInfo.from_type_hint, typ
            )

    def test_invalid_mapping_params(self):
        assert_raises_with_msg(
            DataError,
            "'dict[]' requires exactly 2 arguments, 'dict[int]' has 1.",
            TypeInfo.from_type_hint, 'dict[int]'
        )
        assert_raises_with_msg(
            DataError,
            "'Mapping[]' requires exactly 2 arguments, 'Mapping[x, y, z]' has 3.",
            TypeInfo.from_type_hint, 'Mapping[x,y,z]'
        )

    def test_invalid_tuple_params(self):
        assert_raises_with_msg(
            DataError,
            "Homogenous tuple requires exactly 1 argument, 'tuple[int, str, ...]' has 2.",
            TypeInfo.from_type_hint, 'tuple[int, str, ...]'
        )
        assert_raises_with_msg(
            DataError,
            "Homogenous tuple requires exactly 1 argument, 'tuple[...]' has 0.",
            TypeInfo.from_type_hint, 'tuple[...]'
        )

    def test_params_with_invalid_type(self):
        for name in TYPE_NAMES:
            if TYPE_NAMES[name] not in (list, tuple, dict, set, frozenset):
                assert_raises_with_msg(
                    DataError,
                    f"'{name}' does not accept arguments, '{name}[int]' has 1.",
                    TypeInfo.from_type_hint, f'{name}[int]'
                )

    def test_parameters_with_unknown_type(self):
        info = TypeInfo.from_type_hint('x[int, float]')
        assert_equal([n.type for n in info.nested], [int, float])

    def test_parameters_with_custom_generic(self):
        T = TypeVar('T')

        class Gen(Generic[T]):
            pass

        assert_equal(TypeInfo.from_type_hint(Gen[int]).nested[0].type, int)
        assert_equal(TypeInfo.from_type_hint(Gen[str]).nested[0].type, str)

    def test_non_type(self):
        for item in 42, object(), set(), b'hello':
            info = TypeInfo.from_type_hint(item)
            assert_equal(info.name, str(item))
            assert_equal(info.type, None)

    def test_conversion(self):
        assert_equal(TypeInfo.from_type_hint(int).convert('42'), 42)
        assert_equal(TypeInfo.from_type_hint('list[int]').convert('[42]'), [42])

    def test_failing_conversion(self):
        assert_raises_with_msg(
            ValueError,
            "Argument 'bad' cannot be converted to integer.",
            TypeInfo.from_type_hint(int).convert, 'bad'
        )
        assert_raises_with_msg(
            ValueError,
            "Thingy 't' got value 'bad' that cannot be converted to list[int]: Invalid expression.",
            TypeInfo.from_type_hint('list[int]').convert, 'bad', 't', kind='Thingy'
        )

    def test_custom_converter(self):
        class Custom:
            def __init__(self, arg: int):
                self.arg = arg

            @classmethod
            def from_string(cls, value: str):
                if not value.isdigit():
                    raise ValueError(f'{value} is not good')
                return cls(int(value))

        info = TypeInfo.from_type_hint(Custom)
        converters = {Custom: Custom.from_string}
        result = info.convert('42', custom_converters=converters)
        assert_equal(type(result), Custom)
        assert_equal(result.arg, 42)
        assert_raises_with_msg(
            ValueError,
            "Argument 'bad' cannot be converted to Custom: bad is not good",
            info.convert, 'bad', custom_converters=converters
        )
        assert_raises_with_msg(
            TypeError,
            "Custom converters must be callable, converter for Custom is string.",
            info.convert, '42', custom_converters={Custom: 'bad'}
        )

    def test_no_converter(self):
        assert_raises_with_msg(
            TypeError,
            "No converter found for 'Unknown'.",
            TypeInfo.from_type_hint(type('Unknown', (), {})).convert, 'whatever'
        )
        assert_raises_with_msg(
            TypeError,
            "No converter found for 'unknown[int]'.",
            TypeInfo.from_type_hint('unknown[int]').convert, 'whatever'
        )


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
