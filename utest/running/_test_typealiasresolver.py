import sys
import unittest
from types import NoneType, UnionType
from typing import get_args, get_origin, TypeVar, Union

from robot.running.arguments.typealiasresolver import resolve_type_alias
from robot.utils.asserts import assert_equal, assert_raises

type Forward = SimpleValue
type ForwardUnion = SimpleValue | UnionValue
type SimpleValue = int
type ParamsValue = list[int]
type UnionValue = str | Union[float, None]
type Params[T1, T2] = T1 | T2
type ParamReuse[T] = T | list[T]
type ParamsAndNormal[T] = T | int
type ForwardParams[T1, T2, T3] = T1 | ParamsAndNormal[T2] | Params[T3, None]
type NestedParams[T] = Params[ParamReuse[ParamToScalar[T]], ParamToScalar[bool]]
type ParamToScalar[T] = T
type ParamArg[T] = ParamReuse[tuple[T]]
type UnionArg[T] = ParamReuse[T | None]
if sys.version_info >= (3, 13):
    exec("type ParamDefaults[X, Y=bool, Z=int] = X | Y | list[Z | None]")
else:
    type ParamDefaults[X, Y, Z] = X | Y | list[Z | None]
type Recursive = int | list[Recursive]
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


class TestTypeAliasResolver(unittest.TestCase):

    def test_simple_value(self):
        self._verify(SimpleValue, int)

    def test_params_value(self):
        self._verify(ParamsValue, list, [int])

    def test_union_value(self):
        self._verify(UnionValue, Union, [str, float, NoneType])

    def test_forward_reference(self):
        self._verify(Forward, int)

    def test_forward_reference_with_union(self):
        self._verify(ForwardUnion, Union, [int, str, float, NoneType])

    def test_params(self):
        self._verify(Params[str, int], Union, [str, int])
        self._verify(Params[int, None], Union, [int, NoneType])

    def test_param_reuse(self):
        self._verify(ParamReuse[str], Union, [str, list[str]])

    def test_params_and_normal_values(self):
        self._verify(ParamsAndNormal[str], Union, [str, int])

    def test_nested_params(self):
        self._verify(NestedParams[int], Union, [int, list[int], bool])
        self._verify(NestedParams[str], Union, [str, list[str], bool])

    def test_forward_params(self):
        self._verify(
            ForwardParams[bool, str, float], Union, [bool, str, int, float, NoneType]
        )

    def test_param_to_scalar_value(self):
        self._verify(ParamToScalar[int], int)
        self._verify(ParamToScalar[str], str)
        self._verify(ParamToScalar[list[int]], list, [int])
        self._verify(ParamToScalar[int | str], UnionType, [int, str])

    def test_param_arg(self):
        self._verify(ParamArg[int], Union, [tuple[int], list[tuple[int]]])
        self._verify(ParamArg[str], Union, [tuple[str], list[tuple[str]]])

    def test_union_arg(self):
        self._verify(UnionArg[int], Union, [int, NoneType, list[int | None]])
        self._verify(UnionArg[str], Union, [str, NoneType, list[str | None]])

    @unittest.skipIf(sys.version_info < (3, 13), "Defaults require Python 3.13")
    def test_param_defaults(self):
        self._verify(ParamDefaults[str, int, str], Union, [str, int, list[str | None]])
        self._verify(ParamDefaults[str, int], Union, [str, int, list[int | None]])
        self._verify(ParamDefaults[str], Union, [str, bool, list[int | None]])

    # FIXME: Support recursive type aliases!
    #    def test_recursive(self):
    #        self._verify(Recursive, Union, [])

    def test_unused_param(self):
        self._verify(UnusedParam1[int], int)
        self._verify(UnusedParam1[str], int)
        self._verify(UnusedParam2[str, str], Union, [int, str])

    def test_bad_type_var(self):
        self._fails(BadTypeVar[int], "Type variable 'BAD' has not value.")
        if sys.version_info >= (3, 13):
            self._verify(UglyTypeVar[int], Union, [int, float])

    def test_invalid_usage(self):
        self._verify(Params[1, 2], Union, [1, 2])
        self._verify(Params[int, str, float], Union, [int, str])
        self._fails(Params[int], "Type variable 'T2' has not value.")

    def test_non_existing(self):
        self._fails(NonExisting, "Resolving type alias 'NonExisting' failed: ")

    def test_invalid(self):
        self._fails(Invalid, "Resolving type alias 'Invalid' failed: ")

    def _verify(self, alias, expected_type, expected_args=None):
        value = resolve_type_alias(alias)
        origin = get_origin(value)
        args = get_args(value)
        if expected_args is None:
            assert_equal(value, expected_type)
            assert_equal(args, ())
        else:
            assert_equal(origin, expected_type)
            assert_equal(args, tuple(expected_args))

    def _fails(self, alias, message):
        error = assert_raises(ValueError, resolve_type_alias, alias)
        if not str(error).startswith(message):
            raise AssertionError(
                f"Expected error to start with:\n{message}\n\nGot:\n{error}\n"
            )


if __name__ == "__main__":
    unittest.main()
