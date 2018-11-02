from typing import (List, Sequence, MutableSequence,
                    Dict, Mapping, MutableMapping,
                    Set, MutableSet)


def list_(argument: List, expected=None):
    _validate_type(argument, expected)


def list_with_params(argument: List[int], expected=None):
    _validate_type(argument, expected)


def sequence(argument: Sequence, expected=None):
    _validate_type(argument, expected)


def sequence_with_params(argument: Sequence[bool], expected=None):
    _validate_type(argument, expected)


def mutable_sequence(argument: MutableSequence, expected=None):
    _validate_type(argument, expected)


def mutable_sequence_with_params(argument: MutableSequence[bool], expected=None):
    _validate_type(argument, expected)


def dict_(argument: Dict, expected=None):
    _validate_type(argument, expected)


def dict_with_params(argument: Dict[str, int], expected=None):
    _validate_type(argument, expected)


def mapping(argument: Mapping, expected=None):
    _validate_type(argument, expected)


def mapping_with_params(argument: Mapping[bool, int], expected=None):
    _validate_type(argument, expected)


def mutable_mapping(argument: MutableMapping, expected=None):
    _validate_type(argument, expected)


def mutable_mapping_with_params(argument: MutableMapping[bool, int], expected=None):
    _validate_type(argument, expected)


def set_(argument: Set, expected=None):
    _validate_type(argument, expected)


def set_with_params(argument: Set[bool], expected=None):
    _validate_type(argument, expected)


def mutable_set(argument: MutableSet, expected=None):
    _validate_type(argument, expected)


def mutable_set_with_params(argument: MutableSet[bool], expected=None):
    _validate_type(argument, expected)


def none_as_default(argument: List = None, expected=None):
    _validate_type(argument, expected)


def forward_reference(argument: 'List', expected=None):
    _validate_type(argument, expected)


def forward_ref_with_params(argument: 'List[int]', expected=None):
    _validate_type(argument, expected)


def _validate_type(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        raise AssertionError('%r (%s) != %r (%s)'
                             % (argument, type(argument).__name__,
                                expected, type(expected).__name__))
