from typing import List, Optional, TypedDict

TypedDict.robot_not_keyword = True


class Recursive(TypedDict):
    value: int
    children: List["Recursive"]


class Parent(TypedDict):
    value: int
    child: Optional["Child"]


class Child(TypedDict):
    value: int
    parent: Optional[Parent]


def recursive(argument: Recursive, expected=None):
    _validate(argument, expected)


def mutually_recursive(argument: Parent, expected=None):
    _validate(argument, expected)


def _validate(argument, expected):
    expected = eval(expected)
    if argument != expected:
        raise AssertionError(f"{argument!r} != {expected!r}")
