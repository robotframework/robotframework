# Imports needed for evaluating expected result.
from datetime import datetime, date, timedelta
from decimal import Decimal


def integer(argument: 'Integer', expected=None):
    _validate_type(argument, expected)


def int_(argument: 'INT', expected=None):
    _validate_type(argument, expected)


def long_(argument: 'lOnG', expected=None):
    _validate_type(argument, expected)


def float_(argument: 'Float', expected=None):
    _validate_type(argument, expected)


def double(argument: 'Double', expected=None):
    _validate_type(argument, expected)


def decimal(argument: 'DECIMAL', expected=None):
    _validate_type(argument, expected)


def boolean(argument: 'Boolean', expected=None):
    _validate_type(argument, expected)


def bool_(argument: 'Bool', expected=None):
    _validate_type(argument, expected)


def string(argument: 'String', expected=None):
    _validate_type(argument, expected)


def bytes_(argument: 'BYTES', expected=None):
    _validate_type(argument, expected)


def bytearray_(argument: 'ByteArray', expected=None):
    _validate_type(argument, expected)


def datetime_(argument: 'DateTime', expected=None):
    _validate_type(argument, expected)


def date_(argument: 'Date', expected=None):
    _validate_type(argument, expected)


def timedelta_(argument: 'TimeDelta', expected=None):
    _validate_type(argument, expected)


def list_(argument: 'List', expected=None):
    _validate_type(argument, expected)


def tuple_(argument: 'TUPLE', expected=None):
    _validate_type(argument, expected)


def dictionary(argument: 'Dictionary', expected=None):
    _validate_type(argument, expected)


def dict_(argument: 'Dict', expected=None):
    _validate_type(argument, expected)


def map_(argument: 'Map', expected=None):
    _validate_type(argument, expected)


def set_(argument: 'Set', expected=None):
    _validate_type(argument, expected)


def frozenset_(argument: 'FrozenSet', expected=None):
    _validate_type(argument, expected)


def _validate_type(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        raise AssertionError('%r (%s) != %r (%s)'
                             % (argument, type(argument).__name__,
                                expected, type(expected).__name__))
