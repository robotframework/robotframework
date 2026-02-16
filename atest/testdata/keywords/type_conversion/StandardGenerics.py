from collections.abc import Mapping, MutableMapping, MutableSequence, Sequence
from typing import Union


class Unknown:
    pass


def list_(argument: list[int], expected=None, same=False):
    _validate_type(argument, expected, same)


def list_with_unknown(argument: list[Unknown], expected=None):
    _validate_type(argument, expected)


def list_in_union_1(argument: Union[str, list[str]], expected=None, same=False):
    _validate_type(argument, expected, same)


def list_in_union_2(argument: Union[list[str], str], expected=None, same=False):
    _validate_type(argument, expected, same)


def tuple_(argument: tuple[int, bool, float], expected=None):
    _validate_type(argument, expected)


def tuple_with_unknown(argument: tuple[Unknown, int], expected=None):
    _validate_type(argument, expected)


def tuple_in_union_1(argument: Union[str, tuple[str, str, str]], expected=None):
    _validate_type(argument, expected)


def tuple_in_union_2(argument: Union[tuple[str, str, str], str], expected=None):
    _validate_type(argument, expected)


def homogenous_tuple(argument: tuple[int, ...], expected=None):
    _validate_type(argument, expected)


def homogenous_tuple_with_unknown(argument: tuple[Unknown, ...], expected=None):
    _validate_type(argument, expected)


def homogenous_tuple_in_union_1(argument: Union[str, tuple[str, ...]], expected=None):
    _validate_type(argument, expected)


def homogenous_tuple_in_union_2(argument: Union[tuple[str, ...], str], expected=None):
    _validate_type(argument, expected)


def sequence(argument: Sequence[int], expected=None, same=False):
    _validate_type(argument, expected, same)


def mutable_sequence(argument: MutableSequence[int], expected=None, same=False):
    _validate_type(argument, expected, same)


def dict_(argument: dict[int, float], expected=None, same=False):
    _validate_type(argument, expected, same)


def dict_with_unknown_key(argument: dict[Unknown, int], expected=None):
    _validate_type(argument, expected)


def dict_with_unknown_value(argument: dict[int, Unknown], expected=None):
    _validate_type(argument, expected)


def dict_in_union_1(argument: Union[str, dict[str, str]], expected=None, same=False):
    _validate_type(argument, expected, same)


def dict_in_union_2(argument: Union[dict[str, str], str], expected=None, same=False):
    _validate_type(argument, expected, same)


def mapping(argument: Mapping[int, float], expected=None, same=False):
    _validate_type(argument, expected, same)


def mutable_mapping(argument: MutableMapping[int, float], expected=None, same=False):
    _validate_type(argument, expected, same)


def set_(argument: set[bool], expected=None):
    _validate_type(argument, expected)


def set_with_unknown(argument: set[Unknown], expected=None):
    _validate_type(argument, expected)


def set_in_union_1(argument: Union[str, set[str]], expected=None):
    _validate_type(argument, expected)


def set_in_union_2(argument: Union[set[str], str], expected=None):
    _validate_type(argument, expected)


def nested_generics(argument: list[tuple[int, int]], expected=None, same=False):
    _validate_type(argument, expected, same)


def invalid_list(a: list[int, float]):
    pass


def invalid_tuple(a: tuple[int, float, ...]):
    pass


def invalid_dict(a: dict[int]):
    pass


def invalid_set(a: set[int, float]):
    pass


def _validate_type(argument, expected, same=False):
    if isinstance(expected, str):
        expected = eval(expected)
    if argument != expected or type(argument) is not type(expected):
        a_type = type(argument).__name__
        e_type = type(expected).__name__
        raise AssertionError(f"{argument!r} ({a_type}) != {expected!r} ({e_type})")
    if same and argument is not expected:
        a_id = hex(id(argument))
        e_id = hex(id(expected))
        raise AssertionError(f"{argument!r} (id: {a_id}) != {expected!r} (id: {e_id})")


class CustomSequence(Sequence):

    def __init__(self, data):
        self.data = data

    def __getitem__(self, item):
        return self.data[item]

    def __len__(self):
        return len(self.data)

    def __eq__(self, other):
        return self.data == other.data

    def __str__(self):
        return f"{type(self).__name__}({self.data})"


class CustomMapping(Mapping):

    def __init__(self, data):
        self.data = data

    def __getitem__(self, item):
        return self.data[item]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __str__(self):
        return f"{type(self).__name__}({self.data})"


class NoArgsSequence(CustomSequence):

    def __init__(self):
        super().__init__([])

    @classmethod
    def init(cls, data):
        obj = cls()
        obj.data = data
        return obj


class NoArgsMapping(CustomMapping):

    def __init__(self):
        super().__init__({1: 2.3})

    @classmethod
    def init(cls, data):
        obj = cls()
        obj.data = data
        return obj


def get_variables():
    return {
        "CustomSequence": CustomSequence,
        "CustomMapping": CustomMapping,
        "NoArgsSequence": NoArgsSequence,
        "NoArgsMapping": NoArgsMapping,
    }
