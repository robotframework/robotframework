from collections import abc
from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Flag, Enum, IntFlag, IntEnum
from functools import wraps
from numbers import Integral, Real
from os import PathLike
from pathlib import Path, PurePath

# Needed by `eval()` in `_validate_type()`.
import collections
from fractions import Fraction

from robot.api.deco import keyword


class MyEnum(Enum):
    FOO = 1
    bar = 'xxx'
    foo = 'yyy'
    normalize_me = True


class NoneEnum(Enum):
    NONE = 1
    NTWO = 2
    NTHREE = 3


class MyFlag(Flag):
    RED = 1
    BLUE = 2


class MyIntEnum(IntEnum):
    ON = 1
    OFF = 0


class MyIntFlag(IntFlag):
    R = 4
    W = 2
    X = 1


class Unknown:
    pass


def integer(argument: int, expected=None):
    _validate_type(argument, expected)


def integral(argument: Integral, expected=None):
    _validate_type(argument, expected)


def float_(argument: float, expected=None):
    _validate_type(argument, expected)


def real(argument: Real, expected=None):
    _validate_type(argument, expected)


def decimal(argument: Decimal, expected=None):
    _validate_type(argument, expected)


def boolean(argument: bool, expected=None):
    _validate_type(argument, expected)


def string(argument: str, expected=None):
    _validate_type(argument, expected)


def bytes_(argument: bytes, expected=None):
    _validate_type(argument, expected)


def bytearray_(argument: bytearray, expected=None):
    _validate_type(argument, expected)


def bytestring_replacement(argument: 'bytes | bytearray', expected=None):
    _validate_type(argument, expected)


def datetime_(argument: datetime, expected=None):
    _validate_type(argument, expected)


def date_(argument: date, expected=None):
    _validate_type(argument, expected)


def timedelta_(argument: timedelta, expected=None):
    _validate_type(argument, expected)


def path(argument: Path, expected=None):
    _validate_type(argument, expected)


def pure_path(argument: PurePath, expected=None):
    _validate_type(argument, expected)


def path_like(argument: PathLike, expected=None):
    _validate_type(argument, expected)


def enum_(argument: MyEnum, expected=None):
    _validate_type(argument, expected)


def none_enum(argument: NoneEnum, expected=None):
    _validate_type(argument, expected)


def flag(argument: MyFlag, expected=None):
    _validate_type(argument, expected)


def int_enum(argument: MyIntEnum, expected=None):
    _validate_type(argument, expected)


def int_flag(argument: MyIntFlag, expected=None):
    _validate_type(argument, expected)


def nonetype(argument: type(None), expected=None):
    _validate_type(argument, expected)


def list_(argument: list, expected=None):
    _validate_type(argument, expected)


def sequence(argument: abc.Sequence, expected=None):
    _validate_type(argument, expected)


def mutable_sequence(argument: abc.MutableSequence, expected=None):
    _validate_type(argument, expected)


def tuple_(argument: tuple, expected=None):
    _validate_type(argument, expected)


def dictionary(argument: dict, expected=None):
    _validate_type(argument, expected)


def mapping(argument: abc.Mapping, expected=None):
    _validate_type(argument, expected)


def mutable_mapping(argument: abc.MutableMapping, expected=None):
    _validate_type(argument, expected)


def set_(argument: set, expected=None):
    _validate_type(argument, expected)


def set_abc(argument: abc.Set, expected=None):
    _validate_type(argument, expected)


def mutable_set(argument: abc.MutableSet, expected=None):
    _validate_type(argument, expected)


def frozenset_(argument: frozenset, expected=None):
    _validate_type(argument, expected)


def unknown(argument: Unknown, expected=None):
    _validate_type(argument, expected)


def non_type(argument: 'this is just a random string', expected=None):
    _validate_type(argument, expected)


def unhashable(argument: {}, expected=None):
    _validate_type(argument, expected)


# Causes SyntaxError with `typing.get_type_hints`
def invalid(argument: 'import sys', expected=None):
    _validate_type(argument, expected)


def varargs(*argument: int, expected=None):
    _validate_type(argument, expected)


def kwargs(expected=None, **argument: int):
    _validate_type(argument, expected)


def kwonly(*, argument: float, expected=None):
    _validate_type(argument, expected)


def none_as_default(argument: list = None, expected=None):
    _validate_type(argument, expected)


def none_as_default_with_unknown_type(argument: Unknown = None, expected=None):
    _validate_type(argument, expected)


def forward_referenced_concrete_type(argument: 'int', expected=None):
    _validate_type(argument, expected)


def forward_referenced_abc(argument: 'abc.Sequence', expected=None):
    _validate_type(argument, expected)


def return_value_annotation(argument: int, expected=None) -> float:
    _validate_type(argument, expected)
    return float(argument)


@keyword(types={'argument': timedelta})
def types_via_keyword_deco_override(argument: int, expected=None):
    _validate_type(argument, expected)


@keyword(name='None as types via @keyword disables', types=None)
def none_as_types(argument: int, expected=None):
    _validate_type(argument, expected)


@keyword(name="Empty types via @keyword doesn't override", types=[])
def empty_list_as_types(argument: int, expected=None):
    _validate_type(argument, expected)


@keyword(name="@keyword without types doesn't override")
def keyword_deco_alone_does_not_override(argument: int, expected=None):
    _validate_type(argument, expected)


def decorator(func):
    def wrapper(*args, **kws):
        return func(*args, **kws)
    return wrapper


def decorator_with_wraps(func):
    @wraps(func)
    def wrapper(*args, **kws):
        return func(*args, **kws)
    return wrapper


@decorator
def mismatch_caused_by_decorator(argument: int, expected=None):
    _validate_type(argument, expected)


@decorator_with_wraps
def keyword_with_wraps(argument: int, expected=None):
    _validate_type(argument, expected)


def type_and_default_1(argument: list = None, expected=None):
    _validate_type(argument, expected)


def type_and_default_2(argument: int = True, expected=None):
    _validate_type(argument, expected)


def type_and_default_3(argument: timedelta = 0, expected=None):
    _validate_type(argument, expected)


def type_and_default_4(argument: list = [], expected=None):
    _validate_type(argument, expected)


def _validate_type(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        raise AssertionError('%r (%s) != %r (%s)'
                             % (argument, type(argument).__name__,
                                expected, type(expected).__name__))
