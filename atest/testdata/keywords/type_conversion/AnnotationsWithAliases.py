# Imports needed for evaluating expected result.
from datetime import date, datetime, timedelta  # noqa: F401
from decimal import Decimal  # noqa: F401


def integer(argument: "Integer", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def int_(argument: "INT", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def long_(argument: "lOnG", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def float_(argument: "Float", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def double(argument: "Double", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def decimal(argument: "DECIMAL", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def boolean(argument: "Boolean", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def bool_(argument: "Bool", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def string(argument: "String", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def bytes_(argument: "BYTES", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def bytearray_(argument: "ByteArray", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def datetime_(argument: "DateTime", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def date_(argument: "Date", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def timedelta_(argument: "TimeDelta", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def list_(argument: "List", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def tuple_(argument: "TUPLE", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def dictionary(argument: "Dictionary", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def dict_(argument: "Dict", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def map_(argument: "Map", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def set_(argument: "Set", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def frozenset_(argument: "FrozenSet", expected=None):  # noqa: F821
    _validate_type(argument, expected)


def _validate_type(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    if argument != expected or type(argument) is not type(expected):
        atype = type(argument).__name__
        etype = type(expected).__name__
        raise AssertionError(f"{argument!r} ({atype}) != {expected!r} ({etype})")
