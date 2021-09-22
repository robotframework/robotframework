from enum import Flag, Enum, IntFlag, IntEnum
from datetime import datetime, date, timedelta
from decimal import Decimal

from robot.api.deco import keyword


class MyEnum(Enum):
    FOO = 1
    bar = 'xxx'


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


class Unknown(object):
    pass


def integer(argument=1, expected=None):
    _validate_type(argument, expected)


def float_(argument=-1.0, expected=None):
    _validate_type(argument, expected)


def decimal(argument=Decimal('1.2'), expected=None):
    _validate_type(argument, expected)


def boolean(argument=True, expected=None):
    _validate_type(argument, expected)


def string(argument='', expected=None):
    _validate_type(argument, expected)


def bytes_(argument=b'', expected=None):
    _validate_type(argument, expected)


def bytearray_(argument=bytearray(), expected=None):
    _validate_type(argument, expected)


def datetime_(argument=datetime.now(), expected=None):
    _validate_type(argument, expected)


def date_(argument=date.today(), expected=None):
    _validate_type(argument, expected)


def timedelta_(argument=timedelta(), expected=None):
    _validate_type(argument, expected)


def enum(argument=MyEnum.FOO, expected=None):
    _validate_type(argument, expected)


def flag(argument=MyFlag.RED, expected=None):
    _validate_type(argument, expected)


def int_enum(argument=MyIntEnum.ON, expected=None):
    _validate_type(argument, expected)


def int_flag(argument=MyIntFlag.X, expected=None):
    _validate_type(argument, expected)


def none(argument=None, expected=None):
    _validate_type(argument, expected)


def list_(argument=['mutable', 'defaults', 'are', 'bad'], expected=None):
    _validate_type(argument, expected)


def tuple_(argument=('immutable', 'defaults', 'are', 'ok'), expected=None):
    _validate_type(argument, expected)


def dictionary(argument={'mutable defaults': 'are bad'}, expected=None):
    _validate_type(argument, expected)


def set_(argument={'mutable', 'defaults', 'are', 'bad'}, expected=None):
    _validate_type(argument, expected)


def frozenset_(argument=frozenset({'immutable', 'ok'}), expected=None):
    _validate_type(argument, expected)


def unknown(argument=Unknown(), expected=None):
    _validate_type(argument, expected)


def kwonly(*, argument=0.0, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': timedelta})
def types_via_keyword_deco_override(argument=0, expected=None):
    _validate_type(argument, expected)


@keyword(name='None as types via @keyword disables', types=None)
def none_as_types(argument=0, expected=None):
    _validate_type(argument, expected)


@keyword(name="Empty types via @keyword doesn't override", types=[])
def empty_list_as_types(argument=0, expected=None):
    _validate_type(argument, expected)


@keyword(name="@keyword without types doesn't override")
def keyword_deco_alone_does_not_override(argument=0, expected=None):
    _validate_type(argument, expected)


def _validate_type(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        raise AssertionError('%r (%s) != %r (%s)'
                             % (argument, type(argument).__name__,
                                expected, type(expected).__name__))
