from enum import Enum


class UnknownType(object):
    pass


class Small(Enum):
    one = 1
    two = 2
    three = 3
    four = 4


class Big(Enum):
    A = 1
    B = 2
    C = 3
    D = 4
    E = 5
    F = 6
    G = 7


def A_type_annotation(integer: int, boolean: bool, string: str):
    pass


def B_enum(small: Small, big: Big):
    pass


def C_annotation_and_default(integer: int = 42, list_: list = None, enum: Small = None):
    pass


def D_annotated_kw_only_args(*, kwo: int, with_default: str='value'):
    pass


def E_annotated_varags_and_kwargs(*varargs: int, **kwargs: bool):
    pass


def F_unknown_types(unknown: UnknownType, unrecognized: Ellipsis):
    pass


def G_non_type_annotations(arg: 'One of the usages in PEP-3107',
                           *varargs: 'But surely feels odd...'):
    pass
