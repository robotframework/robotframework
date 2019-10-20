from collections import abc
from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Enum
from functools import wraps
from numbers import Integral, Real

from robot.api.deco import keyword
from robot.utils import DotDict

class MyEnum(Enum):
    FOO = 1
    bar = 'xxx'


class Unknown(object):
    pass


def validate_type(argument, expected):
    if isinstance(expected, str) and expected:
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        raise AssertionError('%r (%s) != %r (%s)'
                             % (argument, type(argument).__name__,
                                expected, type(expected).__name__))