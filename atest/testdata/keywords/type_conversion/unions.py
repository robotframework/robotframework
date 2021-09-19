from numbers import Rational
from typing import List, Optional, Union
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


class MyObject:
    pass


class UnexpectedObject:
    pass


class BadRationalMeta(type(Rational)):
    def __instancecheck__(self, instance):
        raise TypeError('Bang!')


class BadRational(Rational, metaclass=BadRationalMeta):
    pass


def create_my_object():
    return MyObject()


def create_unexpected_object():
    return UnexpectedObject()


def union_of_int_float_and_string(argument: Union[int, float, str], expected):
    assert argument == expected


def union_of_int_and_float(argument: Union[int, float], expected=object()):
    assert argument == expected


def union_with_int_and_none(argument: Union[int, None], expected=object()):
    assert argument == expected


def union_with_int_none_and_str(argument: Union[int, None, str], expected):
    assert argument == expected


def union_with_abc(argument: Union[Rational, None], expected):
    assert argument == expected


def union_with_str_and_abc(argument: Union[str, Rational], expected):
    assert argument == expected


def union_with_subscripted_generics(argument: Union[List[int], int], expected=object()):
    assert argument == eval(expected), '%r != %s' % (argument, expected)


def union_with_subscripted_generics_and_str(argument: Union[List[str], str], expected):
    assert argument == eval(expected), '%r != %s' % (argument, expected)


def union_with_typeddict(argument: Union[TypedDict('X', x=int), None], expected):
    assert argument == eval(expected), '%r != %s' % (argument, expected)


def union_with_item_not_liking_isinstance(argument: Union[BadRational, int], expected):
    assert argument == expected, '%r != %r' % (argument, expected)


def custom_type_in_union(argument: Union[MyObject, str], expected_type):
    assert isinstance(argument, eval(expected_type))


def tuple_of_int_float_and_string(argument: (int, float, str), expected):
    assert argument == expected


def tuple_of_int_and_float(argument: (int, float), expected=object()):
    assert argument == expected


def optional_argument(argument: Optional[int], expected):
    assert argument == expected


def optional_argument_with_default(argument: Optional[float] = None, expected=object()):
    assert argument == expected


def optional_string_with_none_default(argument: Optional[str] = None, expected=object()):
    assert argument == expected


def string_with_none_default(argument: str = None, expected=object()):
    assert argument == expected


def union_with_string_first(argument: Union[str, None], expected):
    assert argument == expected


def union_with_invalid_types(argument: Union['nonex', 'references'], expected):
    assert argument == expected


def tuple_with_invalid_types(argument: ('invalid', 666), expected):
    assert argument == expected
