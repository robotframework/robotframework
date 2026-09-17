import sys
import unittest
from types import NoneType
from typing import get_args, get_origin, TypeVar, Union

from robot.running import TypeInfo
from robot.running.arguments.typealiasresolver import RecursiveAlias, resolve_type_alias
from robot.utils.asserts import assert_equal, assert_raises

type Forward = SimpleValue
type ForwardUnion = SimpleValue | UnionValue
type SimpleValue = int
type ParamsValue = list[int]
type UnionValue = str | Union[float, None]
type Param[T] = list[T]
type Params[T1, T2] = T1 | T2
type ParamReuse[T] = T | list[T]
type ParamsAndNormal[T] = T | int
type ForwardParams[T1, T2, T3] = T1 | ParamsAndNormal[T2] | Params[T3, None]
type NestedParams[T] = Params[ParamReuse[ParamToScalar[T]], ParamToScalar[bool]]
type ParamToScalar[T] = T
type ParamArg[T] = ParamReuse[tuple[T]]
type UnionArg[T] = ParamReuse[T | None]
if sys.version_info >= (3, 13):
    exec("type ParamDefaults[X, Y=bool, Z=int] = X | Y | list[Z | None]")  # noqa
else:
    type ParamDefaults[X, Y, Z] = X | Y | list[Z | None]
type Recursive = int | list[Recursive]
type IndirectlyRecursive = list[Recursive]
type InvalidRecursion = InvalidRecursion
type MutualRecursion = RecursionMutual
type RecursionMutual = MutualRecursion
type UnusedParam1[T] = int
type UnusedParam2[T1, T2] = int | T2
type BadTypeVar[GOOD] = GOOD | BAD | UGLY
type UglyTypeVar[GOOD] = GOOD | UGLY
type NonExisting = NotHere  # noqa: F821
type Invalid = 1 / 0

BAD = TypeVar("BAD")
if sys.version_info >= (3, 13):
    UGLY = TypeVar("UGLY", default=float)
else:
    UGLY = TypeVar("UGLY")


def assert_type(value, expected):
    if get_origin(expected):
        assert_equal(get_origin(value), get_origin(expected))
        assert_equal(get_args(value), get_args(expected))
    else:
        assert_equal(value, expected)


def assert_info(info, expected):
    assert_equal(type(info), type(expected))
    assert_equal(info.name, expected.name)
    assert_equal(info.type, expected.type)
    assert_equal(info.alias, expected.alias)
    if expected.nested is None:
        assert_equal(info.nested, None)
    else:
        for children in zip(info.nested, expected.nested, strict=True):
            assert_info(*children)


class TestTypeAliasResolver(unittest.TestCase):

    def test_simple_value(self):
        self._verify(SimpleValue, int)

    def test_params_value(self):
        self._verify(ParamsValue, list[int])

    def test_union_value(self):
        self._verify(UnionValue, Union[str, float, NoneType])

    def test_forward_reference(self):
        self._verify(Forward, int)

    def test_forward_reference_with_union(self):
        self._verify(ForwardUnion, Union[int, str, float, NoneType])

    def test_params(self):
        self._verify(Param[str], list[str], "Param[str]")
        self._verify(Param[int], list[int], "Param[int]")
        self._verify(Params[str, int], Union[str, int], "Params[str, int]")
        self._verify(Params[int, None], Union[int, NoneType], "Params[int, None]")

    def test_param_reuse(self):
        self._verify(ParamReuse[str], Union[str, list[str]], "ParamReuse[str]")

    def test_params_and_normal_values(self):
        self._verify(ParamsAndNormal[str], Union[str, int], "ParamsAndNormal[str]")

    def test_nested_params(self):
        self._verify(
            NestedParams[int], Union[int, list[int], bool], "NestedParams[int]"
        )
        self._verify(
            NestedParams[str], Union[str, list[str], bool], "NestedParams[str]"
        )

    def test_forward_params(self):
        self._verify(
            ForwardParams[bool, str, float],
            Union[bool, str, int, float, NoneType],
            "ForwardParams[bool, str, float]",
        )

    def test_param_to_scalar_value(self):
        self._verify(ParamToScalar[int], int, "ParamToScalar[int]")
        self._verify(ParamToScalar[str], str, "ParamToScalar[str]")
        self._verify(ParamToScalar[list[int]], list[int], "ParamToScalar[list[int]]")
        self._verify(ParamToScalar[int | str], int | str, "ParamToScalar[int | str]")

    def test_param_arg(self):
        self._verify(
            ParamArg[int], Union[tuple[int], list[tuple[int]]], "ParamArg[int]"
        )
        self._verify(
            ParamArg[str], Union[tuple[str], list[tuple[str]]], "ParamArg[str]"
        )

    def test_union_arg(self):
        self._verify(
            UnionArg[int], Union[int, NoneType, list[int | None]], "UnionArg[int]"
        )
        self._verify(
            UnionArg[str], Union[str, NoneType, list[str | None]], "UnionArg[str]"
        )

    @unittest.skipIf(sys.version_info < (3, 13), "Defaults require Python 3.13")
    def test_param_defaults(self):
        self._verify(
            ParamDefaults[str, int, str],
            Union[str, int, list[str | None]],
            "ParamDefaults[str, int, str]",
        )
        self._verify(
            ParamDefaults[str, int],
            Union[str, int, list[int | None]],
            "ParamDefaults[str, int]",
        )
        self._verify(
            ParamDefaults[str],
            Union[str, bool, list[int | None]],
            "ParamDefaults[str]",
        )

    def test_recursive(self):
        value = resolve_type_alias(Recursive)
        self._verify_recursive(value)
        value = resolve_type_alias(IndirectlyRecursive)
        assert get_origin(value) is list
        self._verify_recursive(*get_args(value))

    def _verify_recursive(self, value):
        assert get_origin(value) is Union
        first, second = get_args(value)
        assert_equal(first, int)
        assert get_origin(second) is list
        (recursive,) = get_args(second)
        assert isinstance(recursive, RecursiveAlias)
        assert_equal(recursive.name, "Recursive")
        assert_equal(recursive.value, Union[first, second])

    def test_invalid_recursion(self):
        error = "Resolving type alias '{}' failed: Invalid recursion."
        self._fails(InvalidRecursion, error.format("InvalidRecursion"))
        self._fails(MutualRecursion, error.format("MutualRecursion"))
        self._fails(RecursionMutual, error.format("RecursionMutual"))

    def test_unused_param(self):
        self._verify(UnusedParam1[int], int, "UnusedParam1[int]")
        self._verify(UnusedParam1[str], int, "UnusedParam1[str]")
        self._verify(UnusedParam2[str, str], Union[int, str], "UnusedParam2[str, str]")

    def test_bad_type_var(self):
        self._fails(BadTypeVar[int], "Type variable 'BAD' has not value.")
        if sys.version_info >= (3, 13):
            self._verify(UglyTypeVar[int], Union[int, float], "UglyTypeVar[int]")

    def test_invalid_usage(self):
        self._verify(Params[1, 2], Union[1, 2], "Params[1, 2]")
        self._verify(Params[int, str, bool], Union[int, str], "Params[int, str, bool]")
        self._fails(Params[int], "Type variable 'T2' has not value.")

    def test_non_existing(self):
        self._fails(NonExisting, "Resolving type alias 'NonExisting' failed: ")

    def test_invalid(self):
        self._fails(Invalid, "Resolving type alias 'Invalid' failed: ")

    def test_alias_in_params(self):
        info = TypeInfo.from_type_hint(list[SimpleValue])
        expected = TypeInfo.from_type_hint(list[int])
        expected.nested[0].alias = "SimpleValue"
        assert_info(info, expected)

    def test_alias_in_union(self):
        info = TypeInfo.from_type_hint(SimpleValue | tuple[Param[ParamToScalar[str]]])
        expected = TypeInfo.from_type_hint(int | tuple[list[str]])
        expected.nested[0].alias = "SimpleValue"
        expected.nested[1].nested[0].alias = "Param[ParamToScalar[str]]"
        assert_info(info, expected)

    def _verify(self, hint, expected_type, alias=None):
        assert_type(resolve_type_alias(hint), expected_type)
        info = TypeInfo.from_type_hint(hint)
        expected = TypeInfo.from_type_hint(expected_type)
        expected.alias = alias or hint.__name__
        assert_info(info, expected)

    def _fails(self, alias, message):
        error = assert_raises(ValueError, resolve_type_alias, alias)
        if not (str(error).startswith(message) and message):
            raise AssertionError(
                f"Expected error to start with:\n{message}\n\nGot:\n{error}\n"
            )


if __name__ == "__main__":
    unittest.main()
