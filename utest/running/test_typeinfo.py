import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import (
    Any, Dict, Generic, List, Literal, Mapping, Sequence, Set, Tuple, TypedDict,
    TypeVar, Union
)

from robot.variables.search import search_variable

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated
try:
    from typing import TypeForm
except ImportError:
    from typing_extensions import TypeForm

from robot.errors import DataError
from robot.running.arguments.typeinfo import TYPE_NAMES, TypeInfo
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
        for name, expected in [
            ("...", Ellipsis),
            ("any", Any),
            ("str", str),
            ("string", str),
            ("unicode", str),
            ("boolean", bool),
            ("bool", bool),
            ("int", int),
            ("integer", int),
            ("long", int),
            ("float", float),
            ("double", float),
            ("decimal", Decimal),
            ("bytes", bytes),
            ("bytearray", bytearray),
            ("datetime", datetime),
            ("date", date),
            ("timedelta", timedelta),
            ("path", Path),
            ("none", type(None)),
            ("list", list),
            ("sequence", list),
            ("tuple", tuple),
            ("dictionary", dict),
            ("dict", dict),
            ("map", dict),
            ("mapping", dict),
            ("set", set),
            ("frozenset", frozenset),
            ("union", Union),
        ]:
            for name in name, name.upper():
                assert_info(TypeInfo(name), name, expected)

    def test_union(self):
        for union in [
            Union[int, str, float],
            (int, str, float),
            [int, str, float],
            Union[int, Union[str, float]],
            (int, [str, float]),
        ]:
            info = TypeInfo.from_type_hint(union)
            assert_equal(info.name, "Union")
            assert_equal(info.is_union, True)
            assert_equal(len(info.nested), 3)
            assert_info(info.nested[0], "int", int)
            assert_info(info.nested[1], "str", str)
            assert_info(info.nested[2], "float", float)

    def test_union_with_one_type_is_reduced_to_the_type(self):
        for union in Union[int], (int,):
            info = TypeInfo.from_type_hint(union)
            assert_info(info, "int", int)
            assert_equal(info.is_union, False)

    def test_empty_union_not_allowed(self):
        for union in Union, ():
            assert_raises_with_msg(
                DataError,
                "Union cannot be empty.",
                TypeInfo.from_type_hint,
                union,
            )

    def test_valid_params(self):
        for typ in (
            List[int],
            Sequence[int],
            Set[int],
            Tuple[int],
            "list[int]",
            "SEQUENCE[INT]",
            "Set[integer]",
            "frozenset[int]",
            "tuple[int]",
        ):
            info = TypeInfo.from_type_hint(typ)
            assert_equal(len(info.nested), 1)
            assert_equal(info.nested[0].type, int)

        for typ in (
            Dict[int, str],
            Mapping[int, str],
            "dict[int, str]",
            "MAP[INTEGER, STRING]",
        ):
            info = TypeInfo.from_type_hint(typ)
            assert_equal(len(info.nested), 2)
            assert_equal(info.nested[0].type, int)
            assert_equal(info.nested[1].type, str)

    def test_generics_without_params(self):
        for typ in List, Sequence, Set, Tuple, Dict, Mapping, list, tuple, dict:
            info = TypeInfo.from_type_hint(typ)
            assert_equal(info.nested, None)

    def test_parameterized_special_form(self):
        info = TypeInfo.from_type_hint(Annotated[int, "xxx"])
        int_info = TypeInfo.from_type_hint(int)
        assert_info(info, "Annotated", Annotated, (int_info, TypeInfo("xxx")))
        info = TypeInfo.from_type_hint(TypeForm[int])
        assert_info(info, "TypeForm", TypeForm, (int_info,))

    def test_invalid_sequence_params(self):
        for typ in "list[int, str]", "SEQUENCE[x, y]", "Set[x, y]", "frozenset[x, y]":
            name = typ.split("[")[0]
            assert_raises_with_msg(
                DataError,
                f"'{name}[]' requires exactly 1 parameter, '{typ}' has 2.",
                TypeInfo.from_type_hint,
                typ,
            )

    def test_invalid_mapping_params(self):
        assert_raises_with_msg(
            DataError,
            "'dict[]' requires exactly 2 parameters, 'dict[int]' has 1.",
            TypeInfo.from_type_hint,
            "dict[int]",
        )
        assert_raises_with_msg(
            DataError,
            "'Mapping[]' requires exactly 2 parameters, 'Mapping[x, y, z]' has 3.",
            TypeInfo.from_type_hint,
            "Mapping[x,y,z]",
        )

    def test_invalid_tuple_params(self):
        assert_raises_with_msg(
            DataError,
            "Homogenous tuple requires exactly 1 parameter, 'tuple[int, str, ...]' has 2.",
            TypeInfo.from_type_hint,
            "tuple[int, str, ...]",
        )
        assert_raises_with_msg(
            DataError,
            "Homogenous tuple requires exactly 1 parameter, 'tuple[...]' has 0.",
            TypeInfo.from_type_hint,
            "tuple[...]",
        )

    def test_params_with_invalid_type(self):
        for name in TYPE_NAMES:
            if TYPE_NAMES[name] not in (list, tuple, dict, set, frozenset, Literal):
                assert_raises_with_msg(
                    DataError,
                    f"'{name}' does not accept parameters, '{name}[int]' has 1.",
                    TypeInfo.from_type_hint,
                    f"{name}[int]",
                )

    def test_parameters_with_unknown_type(self):
        for info in [
            TypeInfo("x", nested=[TypeInfo("int"), TypeInfo("float")]),
            TypeInfo.from_type_hint("x[int, float]"),
        ]:
            assert_info(info, "x", nested=[TypeInfo("int"), TypeInfo("float")])

    def test_parameters_with_custom_generic(self):
        T = TypeVar("T")

        class Gen(Generic[T]):
            pass

        assert_equal(TypeInfo.from_type_hint(Gen[int]).nested[0].type, int)
        assert_equal(TypeInfo.from_type_hint(Gen[str]).nested[0].type, str)

    def test_special_type_hints(self):
        assert_info(TypeInfo.from_type_hint(Any), "Any", Any)
        assert_info(TypeInfo.from_type_hint(Ellipsis), "...", Ellipsis)
        assert_info(TypeInfo.from_type_hint(None), "None", type(None))

    def test_literal(self):
        info = TypeInfo.from_type_hint(Literal["x", 1])
        assert_info(info, "Literal", Literal, (TypeInfo("'x'", "x"), TypeInfo("1", 1)))
        assert_equal(str(info), "Literal['x', 1]")
        info = TypeInfo.from_type_hint(Literal["int", None, True])
        assert_info(
            info,
            "Literal",
            Literal,
            (TypeInfo("'int'", "int"), TypeInfo("None", None), TypeInfo("True", True)),
        )
        assert_equal(str(info), "Literal['int', None, True]")

    def test_from_variable(self):
        info = TypeInfo.from_variable("${x}")
        assert_info(info, None)
        info = TypeInfo.from_variable("${x: int}")
        assert_info(info, "int", int)

    def test_from_variable_list_and_dict(self):
        int_info = TypeInfo.from_type_hint(int)
        any_info = TypeInfo.from_type_hint(Any)
        str_info = TypeInfo.from_type_hint(str)
        info = TypeInfo.from_variable("${x: int}")
        assert_info(info, "int", int)
        info = TypeInfo.from_variable("@{x: int}")
        assert_info(info, "list", list, (int_info,))
        info = TypeInfo.from_variable("&{x: int}")
        assert_info(info, "dict", dict, (any_info, int_info))
        info = TypeInfo.from_variable("&{x: str=int}")
        assert_info(info, "dict", dict, (str_info, int_info))
        match = search_variable("&{x: str=int}", parse_type=True)
        info = TypeInfo.from_variable(match)
        assert_info(info, "dict", dict, (str_info, int_info))

    def test_from_variable_invalid(self):
        assert_raises_with_msg(
            DataError,
            "Unrecognized type 'unknown'.",
            TypeInfo.from_variable,
            "${x: unknown}",
        )
        assert_raises_with_msg(
            DataError,
            "Unrecognized type 'unknown'.",
            TypeInfo.from_variable,
            "${x: list[unknown]}",
        )
        assert_raises_with_msg(
            DataError,
            "Unrecognized type 'unknown'.",
            TypeInfo.from_variable,
            "${x: int|set[unknown]}",
        )
        assert_raises_with_msg(
            DataError,
            "Parsing type 'list[broken' failed: Error at end: Closing ']' missing.",
            TypeInfo.from_variable,
            "${x: list[broken}",
        )
        assert_raises_with_msg(
            DataError,
            "Unrecognized type 'int=float'.",
            TypeInfo.from_variable,
            "${x: int=float}",
        )

    def test_non_type(self):
        for item in 42, object(), set(), b"hello":
            assert_info(TypeInfo.from_type_hint(item), str(item))

    def test_str(self):
        for info, expected in [
            (TypeInfo(), ""),
            (TypeInfo("int"), "int"),
            (TypeInfo("x"), "x"),
            (TypeInfo("list", nested=[TypeInfo("int")]), "list[int]"),
            (TypeInfo("Union", nested=[TypeInfo("x"), TypeInfo("y")]), "x | y"),
            (TypeInfo(nested=()), "[]"),
            (TypeInfo(nested=[TypeInfo("int"), TypeInfo("str")]), "[int, str]"),
        ]:
            assert_equal(str(info), expected)

        for hint in [
            "int",
            "x",
            "int | float",
            "x | y | z",
            "list[int]",
            "tuple[int, ...]",
            "dict[str | int, tuple[int | float]]",
            "x[a, b, c]",
            "Callable[[], None]",
            "Callable[[str, tuple[int | float]], dict[str, int | float]]",
        ]:
            assert_equal(str(TypeInfo.from_type_hint(hint)), hint)

    def test_conversion(self):
        assert_equal(TypeInfo.from_type_hint(int).convert("42"), 42)
        assert_equal(TypeInfo.from_type_hint("list[int]").convert("[4, 2]"), [4, 2])
        assert_equal(
            TypeInfo.from_type_hint('Literal["Dog", "Cat"]').convert("dog"), "Dog"
        )

    def test_no_conversion_needed_with_literal(self):
        converter = TypeInfo.from_type_hint('Literal["Dog", "Cat"]').get_converter()
        assert_equal(converter.no_conversion_needed("Dog"), True)
        assert_equal(converter.no_conversion_needed("dog"), False)
        assert_equal(converter.no_conversion_needed("bad"), False)

    def test_failing_conversion(self):
        assert_raises_with_msg(
            ValueError,
            "Argument 'bad' cannot be converted to integer.",
            TypeInfo.from_type_hint(int).convert,
            "bad",
        )
        assert_raises_with_msg(
            ValueError,
            "Thingy 't' got value 'bad' that cannot be converted to list[int]: "
            "Invalid expression.",
            TypeInfo.from_type_hint("list[int]").convert,
            "bad",
            "t",
            kind="thingy",
        )
        assert_raises_with_msg(
            ValueError,
            "FOR var '${i: int}' got value 'bad' that cannot be converted to integer.",
            TypeInfo.from_variable("${i: int}").convert,
            "bad",
            "${i: int}",
            kind="FOR var",
        )

    def test_custom_converter(self):
        class Custom:
            def __init__(self, arg: int):
                self.arg = arg

            @classmethod
            def from_string(cls, value: str):
                if not value.isdigit():
                    raise ValueError(f"{value} is not good")
                return cls(int(value))

        info = TypeInfo.from_type_hint(Custom)
        converters = {Custom: Custom.from_string}
        result = info.convert("42", custom_converters=converters)
        assert_equal(type(result), Custom)
        assert_equal(result.arg, 42)
        assert_raises_with_msg(
            ValueError,
            "Argument 'bad' cannot be converted to Custom: bad is not good",
            info.convert,
            "bad",
            custom_converters=converters,
        )
        assert_raises_with_msg(
            TypeError,
            "Custom converters must be callable, converter for Custom is string.",
            info.convert,
            "42",
            custom_converters={Custom: "bad"},
        )

    def test_language_config(self):
        info = TypeInfo.from_type_hint(bool)
        assert_equal(info.convert("kyllä", languages="Finnish"), True)
        assert_equal(info.convert("ei", languages=["de", "fi"]), False)

    def test_unknown_converter_is_not_accepted_by_default(self):
        for hint in (
            "Unknown",
            Unknown,
            "dict[str, Unknown]",
            "dict[Unknown, int]",
            "tuple[Unknown, ...]",
            "list[str|Unknown|AnotherUnknown]",
            "list[list[list[list[list[Unknown]]]]]",
            List[Unknown],
            TypedDictWithUnknown,
        ):
            info = TypeInfo.from_type_hint(hint)
            error = "Unrecognized type 'Unknown'."
            assert_raises_with_msg(TypeError, error, info.convert, "whatever")
            assert_raises_with_msg(TypeError, error, info.get_converter)
            converter = info.get_converter(allow_unknown=True)
            assert_raises_with_msg(TypeError, error, converter.validate)

    def test_unknown_converter_can_be_accepted(self):
        for hint in "Unknown", "Unknown[int]", Unknown:
            info = TypeInfo.from_type_hint(hint)
            for value in "hi", 1, None, Unknown():
                converter = info.get_converter(allow_unknown=True)
                assert_equal(converter.convert(value), value)
                assert_equal(info.convert(value, allow_unknown=True), value)

    def test_nested_unknown_converter_can_be_accepted(self):
        for hint in "dict[Unknown, int]", Dict[Unknown, int], TypedDictWithUnknown:
            info = TypeInfo.from_type_hint(hint)
            expected = {"x": 1, "y": 2}
            for value in {"x": "1", "y": 2}, "{'x': '1', 'y': 2}":
                converter = info.get_converter(allow_unknown=True)
                assert_equal(converter.convert(value), expected)
                assert_equal(info.convert(value, allow_unknown=True), expected)
            assert_raises_with_msg(
                ValueError,
                f"Argument 'bad' cannot be converted to {info}: Invalid expression.",
                info.convert,
                "bad",
                allow_unknown=True,
            )


class Unknown:
    pass


class TypedDictWithUnknown(TypedDict):
    x: int
    y: Unknown


if __name__ == "__main__":
    unittest.main()
