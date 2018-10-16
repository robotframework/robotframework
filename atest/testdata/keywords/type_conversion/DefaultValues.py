try:
    from enum import Enum
except ImportError:    # Python < 3.4, unless installed separately
    Enum = object
from datetime import datetime, date, timedelta
from decimal import Decimal

from robot.utils import unicode


class MyEnum(Enum):
    FOO = 1
    bar = 'xxx'


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


def unicode_(argument=u'', expected=None):
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


try:
    exec('''
def kwonly(*, argument=0.0, expected=None):
    _validate_type(argument, expected)
''')
except SyntaxError:
    pass


def _validate_type(argument, expected):
    if isinstance(expected, unicode):
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        raise AssertionError('%r (%s) != %r (%s)'
                             % (argument, type(argument).__name__,
                                expected, type(expected).__name__))
