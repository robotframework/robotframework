"""Library for testing backwards compatibility.

Especially testing argument type information that has been changing after RF 4.
Examples are only using features compatible with all tested versions.
"""

from enum import Enum
from typing import Union
try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict


ROBOT_LIBRARY_VERSION = '1.0'


__all__ = ['simple', 'arguments', 'types', 'special_types', 'union']


class Color(Enum):
    """RGB colors."""
    RED = 'R'
    GREEN = 'G'
    BLUE = 'B'


class Size(TypedDict):
    """Some size."""
    width: int
    height: int


def simple():
    """Some doc.

    Tags: example
    """
    pass


def arguments(a, b=2, *c, d=4, e, **f):
    pass


def types(a: int, b: bool = True):
    pass


def special_types(a: Color, b: Size):
    pass


def union(a: Union[int, float]):
    pass
