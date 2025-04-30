from enum import Enum, IntEnum
from typing import List, Literal


class Char(Enum):
    R = "R"
    F = "F"
    W = "W"


class Number(IntEnum):
    one = 1
    two = 2
    three = 3


def integers(argument: Literal[1, 2, 3], expected=None):
    _validate_type(argument, expected)


def strings(argument: Literal["a", "B", "c"], expected=None):
    _validate_type(argument, expected)


def bytes(argument: Literal[b"a", b"\xe4"], expected=None):
    _validate_type(argument, expected)


def booleans(argument: Literal[True], expected=None):
    _validate_type(argument, expected)


def none(argument: Literal[None], expected=None):
    _validate_type(argument, expected)


def enums(argument: Literal[Char.R, Char.F], expected=None):
    _validate_type(argument, expected)


def int_enums(argument: Literal[Number.one, Number.two], expected=None):
    _validate_type(argument, expected)


def multiple_matches(
    argument: Literal["ABC", "abc", "R", Char.R, Number.one, True, 1, "True", "1"],
    expected=None,
):
    _validate_type(argument, expected)


def in_params(argument: List[Literal["R", "F"]], expected=None):
    _validate_type(argument, expected)


def _validate_type(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    if argument != expected or type(argument) is not type(expected):
        atype = type(argument).__name__
        etype = type(expected).__name__
        raise AssertionError(f"{argument!r} ({atype}) != {expected!r} ({etype})")
