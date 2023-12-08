from typing import TypedDict


TypedDict.robot_not_keyword = True


class StringifiedItems(TypedDict):
    simple: 'int'
    params: 'List[Integer]'
    union: 'int | float'


def parameterized_list(argument: 'list[int]', expected=None):
    assert argument == eval(expected), repr(argument)


def parameterized_dict(argument: 'dict[int, float]', expected=None):
    assert argument == eval(expected), repr(argument)


def parameterized_set(argument: 'set[float]', expected=None):
    assert argument == eval(expected), repr(argument)


def parameterized_tuple(argument: 'tuple[int,float,     str   ]', expected=None):
    assert argument == eval(expected), repr(argument)


def homogenous_tuple(argument: 'tuple[int, ...]', expected=None):
    assert argument == eval(expected), repr(argument)


def literal(argument: "Literal['one', 2, None]", expected=''):
    assert argument == eval(expected), repr(argument)


def union(argument: 'int | float', expected=None):
    assert argument == eval(expected), repr(argument)


def nested(argument: 'dict[int|float, tuple[int, ...] | tuple[int, float]]', expected=None):
    assert argument == eval(expected), repr(argument)


def aliases(a: 'sequence[integer]', b: 'MAPPING[STRING, DOUBLE|None]'):
    assert a == [1, 2, 3]
    assert b == {'1': 1.1, '2': 2.2, '': None}


def typeddict_items(argument: StringifiedItems):
    assert argument['simple'] == 42
    assert argument['params'] == [1, 2, 3]
    assert argument['union'] == 3.14


def invalid(argument: 'bad[info'):
    assert False


def bad_params(argument: 'list[int, str]'):
    assert False
