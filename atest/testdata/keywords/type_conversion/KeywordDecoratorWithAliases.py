# Imports needed for evaluating expected result.
from datetime import datetime, date, timedelta
from decimal import Decimal

from robot.api.deco import keyword


@keyword(types=['Integer'])
def integer(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['INT'])
def int_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': 'lOnG'})
def long_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': 'Float'})
def float_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['Double'])
def double(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['DECIMAL'])
def decimal(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['Boolean'])
def boolean(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['Bool'])
def bool_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['String'])
def string(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['BYTES'])
def bytes_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['ByteArray'])
def bytearray_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['DateTime'])
def datetime_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['Date'])
def date_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['TimeDelta'])
def timedelta_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['List'])
def list_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['TUPLE'])
def tuple_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['Dictionary'])
def dictionary(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['Dict'])
def dict_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['Map'])
def map_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['Set'])
def set_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=['FrozenSet'])
def frozenset_(argument, expected=None):
    _validate_type(argument, expected)


def _validate_type(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        raise AssertionError('%r (%s) != %r (%s)'
                             % (argument, type(argument).__name__,
                                expected, type(expected).__name__))
