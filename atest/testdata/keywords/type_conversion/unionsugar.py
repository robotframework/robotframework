from numbers import Rational
from typing import TypedDict


class MyObject:
    pass


class AnotherObject:
    pass


class BadRationalMeta(type(Rational)):
    def __instancecheck__(self, instance):
        raise TypeError('Bang!')


class BadRational(Rational, metaclass=BadRationalMeta):
    pass


class XD(TypedDict):
    x: int


def create_my_object():
    return MyObject()


def union_of_int_float_and_string(argument: int | float | str, expected):
    assert argument == expected


def union_of_int_and_float(argument: int | float, expected=object()):
    assert argument == expected


def union_with_int_and_none(argument: int | None, expected=object()):
    assert argument == expected


def union_with_int_none_and_str(argument: int | None | str, expected):
    assert argument == expected


def union_with_abc(argument: Rational | None, expected):
    assert argument == expected


def union_with_str_and_abc(argument: str | Rational, expected):
    assert argument == expected


def union_with_subscripted_generics(argument: list[int] | int, expected=object()):
    assert argument == eval(expected), '%r != %s' % (argument, expected)


def union_with_subscripted_generics_and_str(argument: list[str] | str, expected):
    assert argument == eval(expected), '%r != %s' % (argument, expected)


def union_with_typeddict(argument: XD | None, expected):
    assert argument == eval(expected), '%r != %s' % (argument, expected)


def union_with_item_not_liking_isinstance(argument: BadRational | bool, expected):
    assert argument == expected, '%r != %r' % (argument, expected)


def custom_type_in_union(argument: MyObject | str, expected_type):
    assert type(argument).__name__ == expected_type


def only_custom_types_in_union(argument: MyObject | AnotherObject, expected_type):
    assert type(argument).__name__ == expected_type


def union_with_string_first(argument: str | None, expected):
    assert argument == expected
