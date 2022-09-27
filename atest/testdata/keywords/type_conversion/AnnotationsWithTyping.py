from enum import Enum
from typing import (List, Sequence, Tuple, MutableSequence,
                    Dict, Mapping, MutableMapping,
                    Set, MutableSet, Optional)

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

from robot.api.deco import not_keyword


TypedDict = not_keyword(TypedDict)


class BadIntMeta(type(int)):
    def __instancecheck__(self, instance):
        raise TypeError('Bang!')


class BadInt(int, metaclass=BadIntMeta):
    pass


class MyEnum(Enum):
    foo = 1
    bar = 2


def list_(argument: List, expected=None):
    _validate_type(argument, expected)


def list_with_ints(argument: List[int], expected=None):
    _validate_type(argument, expected)
    _validate_list_subtype(argument, expected)


def list_with_enums(argument: List[MyEnum], expected=None):
    _validate_type(argument, expected)
    _validate_list_subtype(argument, expected)


def list_with_ints_or_enums(argument: List[int|MyEnum], expected=None):
    _validate_type(argument, expected)
    _validate_list_subtype(argument, expected)


def sequence(argument: Sequence, expected=None):
    _validate_type(argument, expected)
    _validate_list_subtype(argument, expected)


def sequence_with_params(argument: Sequence[bool], expected=None):
    _validate_type(argument, expected)
    _validate_list_subtype(argument, expected)


def mutable_sequence(argument: MutableSequence, expected=None):
    _validate_type(argument, expected)
    _validate_list_subtype(argument, expected)


def mutable_sequence_with_params(argument: MutableSequence[bool], expected=None):
    _validate_type(argument, expected)
    _validate_list_subtype(argument, expected)


def tuple(argument: Tuple, expected=None):
    _validate_type(argument, expected)
    _validate_list_subtype(argument, expected)


def tuple_with_params(argument: Tuple[int, float, str, MyEnum], expected=None):
    _validate_type(argument, expected)
    _validate_list_subtype(argument, expected)


def tuple_with_ellipsis(argument: Tuple[int, ...], expected=None):
    _validate_type(argument, expected)
    _validate_list_subtype(argument, expected)


def dict_(argument: Dict, expected=None):
    _validate_type(argument, expected)
    _validate_dict_subtypes(argument, expected)


def dict_with_str_int(argument: Dict[str, int], expected=None):
    _validate_type(argument, expected)
    _validate_dict_subtypes(argument, expected)


def dict_with_enums(argument: Dict[MyEnum, bool], expected=None):
    _validate_type(argument, expected)
    _validate_dict_subtypes(argument, expected)


def typeddict(argument: TypedDict('X', x=int), expected=None):
    _validate_type(argument, expected)
    _validate_dict_subtypes(argument, expected)


def mapping(argument: Mapping, expected=None):
    _validate_type(argument, expected)
    _validate_dict_subtypes(argument, expected)


def mapping_with_params(argument: Mapping[bool, int], expected=None):
    _validate_type(argument, expected)
    _validate_dict_subtypes(argument, expected)


def mutable_mapping(argument: MutableMapping, expected=None):
    _validate_type(argument, expected)
    _validate_dict_subtypes(argument, expected)


def mutable_mapping_with_params(argument: MutableMapping[bool, int], expected=None):
    _validate_type(argument, expected)
    _validate_dict_subtypes(argument, expected)


def set_(argument: Set, expected=None):
    _validate_type(argument, expected)
    _validate_set_subtype(argument, expected)


def set_with_bool(argument: Set[bool], expected=None):
    _validate_type(argument, expected)
    _validate_set_subtype(argument, expected)


def set_with_enum(argument: Set[MyEnum], expected=None):
    _validate_type(argument, expected)
    _validate_set_subtype(argument, expected)


def mutable_set(argument: MutableSet, expected=None):
    _validate_type(argument, expected)
    _validate_set_subtype(argument, expected)


def mutable_set_with_params(argument: MutableSet[MyEnum], expected=None):
    _validate_type(argument, expected)
    _validate_set_subtype(argument, expected)


def optional_int(argument: Optional[int]=None, expected=None):
    _validate_type(argument, expected)


def optional_enum(argument: Optional[MyEnum], expected=None):
    _validate_type(argument, expected)


def none_as_default(argument: List = None, expected=None):
    _validate_type(argument, expected)


def forward_reference(argument: 'List', expected=None):
    _validate_type(argument, expected)


def forward_ref_with_params(argument: 'List[int]', expected=None):
    _validate_type(argument, expected)


def not_liking_isinstance(argument: BadInt, expected=None):
    _validate_type(argument, expected)


def _validate_type(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        raise AssertionError(f"{repr(argument)} ({type(argument).__name__}) ≠ "
                             f"{repr(expected)} ({type(expected).__name__})")


def _validate_list_subtype(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    for i in range(len(expected)):
        if argument[i] != expected[i] or type(argument[i]) != type(expected[i]):
            raise AssertionError(f"{repr(argument[i])} ({type(argument[i]).__name__}) ≠"
                                 f" {repr(expected[i])} ({type(expected[i]).__name__})")


def _validate_dict_subtypes(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    for k in expected:
        if k not in argument:
            raise AssertionError(f"expected key {repr(k)} ({type(k).__name__}) "
                                 f"not present in {repr(argument)}")
        if argument[k] != expected[k] or type(argument[k]) != type(expected[k]):
            raise AssertionError(f"{repr(argument[k])} ({type(argument[k]).__name__}) ≠"
                                 f" {repr(expected[k])} ({type(expected[k]).__name__})")


def _validate_set_subtype(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    for i in expected:
        if i not in argument:
            raise AssertionError(f"{repr(i)} ({type(i).__name__})"
                                 f" not in {repr(expected)}")
