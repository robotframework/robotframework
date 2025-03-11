from datetime import date, timedelta
from collections.abc import Mapping
from numbers import Rational
from typing import List, Optional, TypedDict, Union


class MyObject:
    pass


class AnotherObject:
    pass


class BadRationalMeta(type(Rational)):
    def __instancecheck__(self, instance):
        raise TypeError('Bang!')


class XD(TypedDict):
    x: int


class BadRational(Rational, metaclass=BadRationalMeta):
    pass


def create_my_object():
    return MyObject()


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


def union_with_typeddict(argument: Union[XD, None], expected):
    assert argument == eval(expected), '%r != %s' % (argument, expected)


def union_with_str_and_typeddict(argument: Union[str, XD], expected, non_dict_mapping=False):
    if non_dict_mapping:
        assert isinstance(argument, Mapping) and not isinstance(argument, dict)
        argument = dict(argument)
    assert argument == eval(expected), '%r != %s' % (argument, expected)


def union_with_item_not_liking_isinstance(argument: Union[BadRational, int], expected):
    assert argument == expected, '%r != %r' % (argument, expected)


def union_with_multiple_types(argument: Union[int, float, None, date, timedelta], expected=object()):
    assert argument == expected, '%r != %r' % (argument, expected)


def unrecognized_type(argument: Union[MyObject, str], expected_type):
    assert type(argument).__name__ == expected_type


def only_unrecognized_types(argument: Union[MyObject, AnotherObject], expected_type):
    assert type(argument).__name__ == expected_type


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


def incompatible_default(argument: Union[None, int] = 1.1, expected=object()):
    assert argument == expected


def unrecognized_type_with_incompatible_default(argument: Union[MyObject, int] = 1.1,
                                                expected=object()):
    assert argument == expected


def union_with_invalid_types(argument: Union['nonex', 'references'], expected):
    assert argument == expected


def tuple_with_invalid_types(argument: ('invalid', 666), expected):
    assert argument == expected


def union_without_types(argument: Union):
    assert False


def empty_tuple(argument: ()):
    assert False
