from typing import (Any, Dict, List, Mapping, MutableMapping, MutableSet, MutableSequence,
                    Set, Sequence, Tuple, Union)
try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict

from robot.api.deco import not_keyword


TypedDict = not_keyword(TypedDict)


class Point2D(TypedDict):
    x: int
    y: int


class Point(Point2D, total=False):
    z: int


class BadIntMeta(type(int)):
    def __instancecheck__(self, instance):
        raise TypeError('Bang!')


class BadInt(int, metaclass=BadIntMeta):
    pass


def list_(argument: List, expected=None):
    _validate_type(argument, expected)


def list_with_types(argument: List[int], expected=None):
    _validate_type(argument, expected)


def tuple_(argument: Tuple, expected=None):
    _validate_type(argument, expected)


def tuple_with_types(argument: Tuple[bool, int], expected=None):
    _validate_type(argument, expected)


def homogenous_tuple(argument: Tuple[int, ...], expected=None):
    _validate_type(argument, expected)


def sequence(argument: Sequence, expected=None):
    _validate_type(argument, expected)


def sequence_with_types(argument: Sequence[Union[int, float]], expected=None):
    _validate_type(argument, expected)


def mutable_sequence(argument: MutableSequence, expected=None):
    _validate_type(argument, expected)


def mutable_sequence_with_types(argument: MutableSequence[int], expected=None):
    _validate_type(argument, expected)


def dict_(argument: Dict, expected=None):
    _validate_type(argument, expected)


def dict_with_types(argument: Dict[int, float], expected=None):
    _validate_type(argument, expected)


def mapping(argument: Mapping, expected=None):
    _validate_type(argument, expected)


def mapping_with_types(argument: Mapping[int, float], expected=None):
    _validate_type(argument, expected)


def mutable_mapping(argument: MutableMapping, expected=None):
    _validate_type(argument, expected)


def mutable_mapping_with_types(argument: MutableMapping[int, float], expected=None):
    _validate_type(argument, expected)


def typeddict(argument: Point2D, expected=None):
    _validate_type(argument, expected)


def typeddict_with_optional(argument: Point, expected=None):
    _validate_type(argument, expected)


def set_(argument: Set, expected=None):
    _validate_type(argument, expected)


def set_with_types(argument: Set[int], expected=None):
    _validate_type(argument, expected)


def mutable_set(argument: MutableSet, expected=None):
    _validate_type(argument, expected)


def mutable_set_with_types(argument: MutableSet[float], expected=None):
    _validate_type(argument, expected)


def any_(argument: Any = 1, expected=None):
    _validate_type(argument, expected)


def none_as_default(argument: List = None, expected=None):
    _validate_type(argument, expected)


def none_as_default_with_any(argument: Any = None, expected=None):
    _validate_type(argument, expected)


def forward_reference(argument: 'List', expected=None):
    _validate_type(argument, expected)


def forward_ref_with_types(argument: 'List[int]', expected=None):
    _validate_type(argument, expected)


def not_liking_isinstance(argument: BadInt, expected=None):
    _validate_type(argument, expected)


def _validate_type(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        atype = type(argument).__name__
        etype = type(expected).__name__
        raise AssertionError(f'{argument!r} ({atype}) != {expected!r} ({etype})')
