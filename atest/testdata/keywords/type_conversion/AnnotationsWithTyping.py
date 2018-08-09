from typing import Dict, List, Set, Iterable, Mapping


def dict_(argument: Dict, expected=None):
    _validate_type(argument, expected)


def dict_with_params(argument: Dict[str, int], expected=None):
    _validate_type(argument, expected)


def list_(argument: List, expected=None):
    _validate_type(argument, expected)


def list_with_params(argument: List[int], expected=None):
    _validate_type(argument, expected)


def set_(argument: Set, expected=None):
    _validate_type(argument, expected)


def set_with_params(argument: Set[bool], expected=None):
    _validate_type(argument, expected)


def iterable(argument: Iterable, expected=None):
    _validate_type(argument, expected)


def iterable_with_params(argument: Iterable[bool], expected=None):
    _validate_type(argument, expected)


def mapping(argument: Mapping, expected=None):
    _validate_type(argument, expected)


def mapping_with_params(argument: Mapping[bool, int], expected=None):
    _validate_type(argument, expected)


def _validate_type(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        raise AssertionError('%r (%s) != %r (%s)'
                             % (argument, type(argument).__name__,
                                expected, type(expected).__name__))
