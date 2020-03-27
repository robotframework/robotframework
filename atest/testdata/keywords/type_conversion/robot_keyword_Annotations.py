from datetime import datetime, date, timedelta
from decimal import Decimal
from functools import wraps
from numbers import Integral, Real

from robot.api.deco import keyword
from robot.utils import DotDict

def validate_type(argument, expected):
    if isinstance(expected, str) and expected:
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        raise AssertionError('%r (%s) != %r (%s)'
                             % (argument, type(argument).__name__,
                                expected, type(expected).__name__))
