try:
    from collections import abc
except ImportError:
    import collections as abc
from datetime import datetime, date, timedelta
from decimal import Decimal
try:
    from enum import Enum
except ImportError:
    class Enum(object):
        pass
from numbers import Integral, Real

from robot.api.deco import keyword
from robot.utils import PY2, PY3, unicode


class MyEnum(Enum):
    FOO = 1
    bar = 'xxx'
    foo = 'yyy'
    normalize_me = True


class Unknown(object):
    pass


@keyword(types={'argument': int})
def integer(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': Integral})
def integral(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': float})
def float_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': Real})
def real(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': Decimal})
def decimal(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': bool})
def boolean(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': unicode})
def string(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': bytes})
def bytes_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': getattr(abc, 'ByteString', None)})
def bytestring(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': bytearray})
def bytearray_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': datetime})
def datetime_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': date})
def date_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': timedelta})
def timedelta_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': MyEnum})
def enum_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': type(None)})
def nonetype(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': None})
def none(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': list})
def list_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': abc.Sequence})
def sequence(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': abc.MutableSequence})
def mutable_sequence(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': tuple})
def tuple_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': dict})
def dictionary(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': abc.Mapping})
def mapping(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': abc.MutableMapping})
def mutable_mapping(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': set})
def set_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': abc.Set})
def set_abc(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': abc.MutableSet})
def mutable_set(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': frozenset})
def frozenset_(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': Unknown})
def unknown(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': 'this is string, not type'})
def non_type(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types={'argument': int})
def varargs(*argument, **expected):
    expected = expected.pop('expected', None)
    _validate_type(argument, expected)


@keyword(types={'argument': int})
def kwargs(expected=None, **argument):
    _validate_type(argument, expected)


if PY3:
    exec('''
@keyword(types={'argument': float})
def kwonly(*, argument, expected=None):
    _validate_type(argument, expected)
''')


@keyword(types='invalid')
def invalid_type_spec():
    raise RuntimeError('Should not be executed')


@keyword(types={'no_match': int, 'xxx': 42})
def non_matching_name(argument):
    raise RuntimeError('Should not be executed')


@keyword(types={'argument': int, 'return': float})
def return_type(argument, expected=None):
    _validate_type(argument, expected)


@keyword(types=[list])
def type_and_default_1(argument=None, expected=None):
    _validate_type(argument, expected)


@keyword(types=[int])
def type_and_default_2(argument=True, expected=None):
    _validate_type(argument, expected)


@keyword(types=[timedelta])
def type_and_default_3(argument=0, expected=None):
    _validate_type(argument, expected)


if PY3:
    exec('''
from typing import Union

@keyword(types={'argument': Union[int, None, float]})
def multiple_types_using_union(argument, expected=None):
    _validate_type(argument, expected)
''')


@keyword(types={'argument': (int, None, float)})
def multiple_types_using_tuple(argument, expected=None):
    _validate_type(argument, expected)


def _validate_type(argument, expected):
    if isinstance(expected, unicode):
        if PY2 and expected[0] in '\'"' and expected[0] == expected[-1]:
            expected = 'u' + expected
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        raise AssertionError('%r (%s) != %r (%s)'
                             % (argument, type(argument).__name__,
                                expected, type(expected).__name__))
