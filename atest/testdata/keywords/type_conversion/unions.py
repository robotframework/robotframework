from typing import Optional, Union

class MyObject(object):
    def __init__(self):
        pass

class UnexpectedObject(object):
    def __init__(self):
        pass

def with_optional_argument(arg: Optional[int], expected='unexpected'):
    assert arg == expected

def unescaped_optionalism(arg: Optional[float]=None):
    assert isinstance(arg, float)

def union_of_int_float_and_string(arg: Union[int, float, str], expected):
    assert arg == expected

def create_my_object():
    return MyObject()

def create_unexpected_object():
    return UnexpectedObject()

def custom_type_in_union(arg: Union[MyObject, str], expected_type):
    assert str(type(arg)) == expected_type, str(type(arg))+expected_type