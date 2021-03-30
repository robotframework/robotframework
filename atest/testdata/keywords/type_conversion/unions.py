from typing import Optional, Union


class MyObject(object):
    def __init__(self):
        pass


class UnexpectedObject(object):
    def __init__(self):
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
