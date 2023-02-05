from typing import Union

from typing_extensions import overload


@overload
def foo(argument: int, expected: object): ...


@overload
def foo(argument: None, expected: object): ...


def foo(argument: Union[int, None], expected: object):
    assert argument == expected


@overload
def bar(argument: int, expected: object): ...


@overload
def bar(argument: None, expected: object): ...


def bar(argument, expected):
    assert argument == expected
