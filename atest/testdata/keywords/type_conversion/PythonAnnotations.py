from enum import Enum


class Foo(Enum):
    BAR = 1


class Unknown(object):
    pass


def integer(argument: int, expected=None):
    _validate_type(argument, expected)


def float_(argument: float, expected=None):
    _validate_type(argument, expected)


def boolean(argument: bool, expected=None):
    _validate_type(argument, expected)


def list_(argument: list, expected=None):
    _validate_type(argument, expected)


def tuple_(argument: tuple, expected=None):
    _validate_type(argument, expected)


def dictionary(argument: dict, expected=None):
    _validate_type(argument, expected)


def set_(argument: set, expected=None):
    _validate_type(argument, expected)


def enum_(argument: Foo, expected=None):
    _validate_type(argument, expected)


def bytes_(argument: bytes, expected=None):
    _validate_type(argument, expected)


def unknown(argument: Unknown, expected=None):
    _validate_type(argument, expected)


def _validate_type(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        raise AssertionError('%r (%s) != %r (%s)'
                             % (argument, type(argument).__name__,
                                expected, type(expected).__name__))
