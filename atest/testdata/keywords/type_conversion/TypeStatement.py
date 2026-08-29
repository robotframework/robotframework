import sys
from enum import Enum
from typing import TypedDict

TypedDict.robot_not_keyword = True


class Toggle(Enum):
    ON = "ON"
    OFF = "OFF"


class Point(TypedDict):
    x: int
    y: int


type ForwardRef = SimpleValue
type GenericForwardRef[T] = GenericParams[T]
type SimpleValue = int
type ParamsValue = list[int]
type UnionValue = int | float
type EnumValue = Toggle
type TypedDictValue = Point
type Recursive = int | list[Recursive]
type GenericSimple[T] = T
type GenericParams[T] = list[T]
type GenericUnion[X, Y] = X | Y
if sys.version_info >= (3, 13):
    exec("type GenericDefaults[X, Y=None] = X | Y")
else:
    type GenericDefaults[X, Y] = X | Y
type Invalid = NonExisting  # noqa: F821


def simple_value(argument: SimpleValue, expected: int):
    assert isinstance(argument, int)
    assert argument == expected


def params_value(argument: ParamsValue, expected: list[int]):
    assert isinstance(argument, list)
    assert all(isinstance(i, int) for i in argument)
    assert argument == expected


def union_value(argument: UnionValue, expected: int | float):
    assert isinstance(argument, type(expected))
    assert argument == expected


def enum_value(argument: EnumValue, expected: Toggle):
    assert isinstance(argument, Toggle)
    assert argument is expected


def typed_dict_value(argument: TypedDictValue, expected: Point):
    assert isinstance(argument, dict)
    assert argument == expected


def forward_ref(argument: ForwardRef, expected: int):
    simple_value(argument, expected)


def recursive(argument: Recursive, expected: int | list = -1):
    assert isinstance(argument, type(expected))
    assert argument == expected


def generic_simple(argument: GenericSimple[int], expected: int):
    simple_value(argument, expected)


def generic_params(argument: GenericParams[int], expected: list[int]):
    params_value(argument, expected)


def generic_union(argument: GenericUnion[int, float], expected: int | float):
    union_value(argument, expected)


def generic_defaults_1(argument: GenericDefaults[int], expected: int | None):
    assert isinstance(argument, type(expected))
    assert argument == expected


def generic_defaults_2(argument: GenericDefaults[int, float], expected: int | float):
    assert isinstance(argument, type(expected))
    assert argument == expected


def generic_forward_ref(argument: GenericForwardRef[int], expected: list[int]):
    params_value(argument, expected)


def alias_as_param(argument: list[SimpleValue], expected: list[int]):
    params_value(argument, expected)


def alias_in_union(
    argument: SimpleValue | GenericParams[int], expected: int | list[int]
):
    if isinstance(expected, int):
        assert isinstance(argument, int)
        simple_value(argument, expected)
    else:
        assert isinstance(argument, list)
        params_value(argument, expected)


def invalid(argument: Invalid):
    pass
