import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import (Any, Dict, Generic, List, Literal, Mapping, Sequence, Set, Tuple,
                    TypeVar, Union)

from robot.errors import DataError
from robot.running.arguments.typeinfo import TypeInfo, TYPE_NAMES
from robot.utils.asserts import assert_equal, assert_raises_with_msg


def assert_info(info: TypeInfo, name, type=None, nested=None):
    assert_equal(info.name, name, info)
    assert_equal(info.type, type, info)
    if nested is None:
        assert_equal(info.nested, None)
    else:
        assert_equal(len(info.nested), len(nested))
        for child, exp in zip(info.nested, nested):
            assert_info(child, exp.name, exp.type, exp.nested)


class TestTypeInfo(unittest.TestCase):

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
                assert_info(TypeInfo(name), name, expected)

    def test_union(self):
        for union in [Union[int, str, float],
                      (int, str, float),
                      [int, str, float],
                      Union[int, Union[str, float]],
                      (int, [str, float])]:
            info = TypeInfo.from_type_hint(union)
            assert_equal(info.name, 'Union')
            assert_equal(info.is_union, True)
            assert_equal(len(info.nested), 3)
            assert_info(info.nested[0], 'int', int)
            assert_info(info.nested[1], 'str', str)
            assert_info(info.nested[2], 'float', float)

    def test_union_with_one_type_is_reduced_to_the_type(self):
        for union in Union[int], (int,):
            info = TypeInfo.from_type_hint(union)
            assert_info(info, 'int', int)
            assert_equal(info.is_union, False)

    def test_empty_union_not_allowed(self):
        for union in Union, ():
            assert_raises_with_msg(
                DataError, 'Union cannot be empty.',
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

    def test_generics_without_params(self):
        for typ in List, Sequence, Set, Tuple, Dict, Mapping, list, tuple, dict:
            info = TypeInfo.from_type_hint(typ)
            assert_equal(info.nested, None)

    def test_invalid_sequence_params(self):
        for typ in 'list[int, str]', 'SEQUENCE[x, y]', 'Set[x, y]', 'frozenset[x, y]':
            name = typ.split('[')[0]
            assert_raises_with_msg(
                DataError,
                f"'{name}[]' requires exactly 1 parameter, '{typ}' has 2.",
                TypeInfo.from_type_hint, typ
            )

    def test_invalid_mapping_params(self):
        assert_raises_with_msg(
            DataError,
            "'dict[]' requires exactly 2 parameters, 'dict[int]' has 1.",
            TypeInfo.from_type_hint, 'dict[int]'
        )
        assert_raises_with_msg(
            DataError,
            "'Mapping[]' requires exactly 2 parameters, 'Mapping[x, y, z]' has 3.",
            TypeInfo.from_type_hint, 'Mapping[x,y,z]'
        )

    def test_invalid_tuple_params(self):
        assert_raises_with_msg(
            DataError,
            "Homogenous tuple requires exactly 1 parameter, 'tuple[int, str, ...]' has 2.",
            TypeInfo.from_type_hint, 'tuple[int, str, ...]'
        )
        assert_raises_with_msg(
            DataError,
            "Homogenous tuple requires exactly 1 parameter, 'tuple[...]' has 0.",
            TypeInfo.from_type_hint, 'tuple[...]'
        )

    def test_params_with_invalid_type(self):
        for name in TYPE_NAMES:
            if TYPE_NAMES[name] not in (list, tuple, dict, set, frozenset, Literal):
                assert_raises_with_msg(
                    DataError,
                    f"'{name}' does not accept parameters, '{name}[int]' has 1.",
                    TypeInfo.from_type_hint, f'{name}[int]'
                )

    def test_parameters_with_unknown_type(self):
        for info in [TypeInfo('x', nested=[TypeInfo('int'), TypeInfo('float')]),
                     TypeInfo.from_type_hint('x[int, float]')]:
            assert_info(info, 'x', nested=[TypeInfo('int'), TypeInfo('float')])

    def test_parameters_with_custom_generic(self):
        T = TypeVar('T')

        class Gen(Generic[T]):
            pass

        assert_equal(TypeInfo.from_type_hint(Gen[int]).nested[0].type, int)
        assert_equal(TypeInfo.from_type_hint(Gen[str]).nested[0].type, str)

    def test_special_type_hints(self):
        assert_info(TypeInfo.from_type_hint(Any), 'Any', Any)
        assert_info(TypeInfo.from_type_hint(Ellipsis), '...', Ellipsis)
        assert_info(TypeInfo.from_type_hint(None), 'None', type(None))

    def test_literal(self):
        info = TypeInfo.from_type_hint(Literal['x', 1])
        assert_info(info, 'Literal', Literal, (TypeInfo("'x'", 'x'),
                                               TypeInfo('1', 1)))
        assert_equal(str(info), "Literal['x', 1]")
        info = TypeInfo.from_type_hint(Literal['int', None, True])
        assert_info(info, 'Literal', Literal, (TypeInfo("'int'", 'int'),
                                               TypeInfo('None', None),
                                               TypeInfo('True', True)))
        assert_equal(str(info), "Literal['int', None, True]")

    def test_non_type(self):
        for item in 42, object(), set(), b'hello':
            assert_info(TypeInfo.from_type_hint(item), str(item))

    def test_str(self):
        for info, expected in [
            (TypeInfo(), ''), (TypeInfo('int'), 'int'),  (TypeInfo('x'), 'x'),
            (TypeInfo('list', nested=[TypeInfo('int')]), 'list[int]'),
            (TypeInfo('Union', nested=[TypeInfo('x'), TypeInfo('y')]), 'x | y'),
            (TypeInfo(nested=()), '[]'),
            (TypeInfo(nested=[TypeInfo('int'), TypeInfo('str')]), '[int, str]')
        ]:
            assert_equal(str(info), expected)
        for hint in [
            'int', 'x', 'int | float', 'x | y | z', 'list[int]', 'tuple[int, ...]',
            'dict[str | int, tuple[int | float]]', 'x[a, b, c]', 'Callable[[], None]',
            'Callable[[str, tuple[int | float]], dict[str, int | float]]'
        ]:
            assert_equal(str(TypeInfo.from_type_hint(hint)), hint)

    def test_conversion(self):
        assert_equal(TypeInfo.from_type_hint(int).convert('42'), 42)
        assert_equal(TypeInfo.from_type_hint('list[int]').convert('[4, 2]'), [4, 2])

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

    def test_language_config(self):
        info = TypeInfo.from_type_hint(bool)
        assert_equal(info.convert('kyllä', languages='Finnish'), True)
        assert_equal(info.convert('ei', languages=['de', 'fi']), False)

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


if __name__ == '__main__':
    unittest.main()
