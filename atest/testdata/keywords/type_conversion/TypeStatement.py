import sys

type ForwardRef = SimpleValue
type GenericForwardRef[T] = GenericParams[T]
type SimpleValue = int
type ParamsValue = list[int]
type UnionValue = int | float
type Recursive = int | list[Recursive]
type GenericSimple[T] = T
type GenericParams[T] = list[T]
type GenericUnion[X, Y] = X | Y
if sys.version_info >= (3, 13):
    exec("type GenericDefaults[X, Y=None] = X | Y")
else:
    type GenericDefaults[X, Y] = X | Y
type Invalid = NonExisting  # noqa: F821


def simple_value(arg: SimpleValue, expected: int):
    assert isinstance(arg, int)
    assert arg == expected


def params_value(arg: ParamsValue, expected: list[int]):
    assert isinstance(arg, list)
    assert all(isinstance(i, int) for i in arg)
    assert arg == expected


def union_value(arg: UnionValue, expected: int | float):
    assert isinstance(arg, type(expected))
    assert arg == expected


def forward_ref(arg: ForwardRef, expected: int):
    simple_value(arg, expected)


def recursive(argument: Recursive, expected: int | list = -1):
    assert isinstance(argument, type(expected))
    assert argument == expected


def generic_simple(arg: GenericSimple[int], expected: int):
    simple_value(arg, expected)


def generic_params(arg: GenericParams[int], expected: list[int]):
    params_value(arg, expected)


def generic_union(arg: GenericUnion[int, float], expected: int | float):
    union_value(arg, expected)


def generic_defaults_1(arg: GenericDefaults[int], expected: int | None):
    assert isinstance(arg, type(expected))
    assert arg == expected


def generic_defaults_2(arg: GenericDefaults[int, float], expected: int | float):
    assert isinstance(arg, type(expected))
    assert arg == expected


def generic_forward_ref(arg: GenericForwardRef[int], expected: list[int]):
    params_value(arg, expected)


def invalid(arg: Invalid):
    pass
