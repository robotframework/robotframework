from __future__ import annotations
from collections.abc import Mapping
from numbers import Integral
from typing import List


def concrete_types(a: int, b: bool, c: list):
    assert a == 42, repr(a)
    assert b is False, repr(b)
    assert c == [1, 'kaksi'], repr(c)


def abcs(a: Integral, b: Mapping):
    assert a == 42, repr(a)
    assert b == {'key': 'value'}, repr(b)


def typing_(a: List, b: List[int]):
    assert a == ['foo', 'bar'], repr(a)
    assert b == [1, 2, 3], repr(b)


# These cause exception with `typing.get_type_hints`
def invalid1(a: foo):
    assert a == 'xxx'


def invalid2(a: 1/0):
    assert a == 'xxx'
