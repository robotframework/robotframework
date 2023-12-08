from enum import Enum
from typing import Any, Dict, List, Literal, Union, Tuple


class UnknownType:
    pass


class Small(Enum):
    one = 1
    two = 2
    three = 3
    four = 4


class ManySmall(Enum):
    A = 'a'
    B = 'b'
    C = 'c'
    D = 'd'
    E = 'd'
    F = 'e'
    G = 'g'
    H = 'h'
    I = 'i'
    J = 'j'
    K = 'k'


class Big(Enum):
    FIRST_MEMBER_IS_LONG = 1
    SECOND_MEMBER_IS_LONGER = 2
    THIRD_MEMBER_IS_THE_LONGEST = 3
    FOURTH_IS_SHORT = 4


def A_type_annotation(integer: int, boolean: bool, string: str):
    pass


def B_enum(small: Small, many_small: ManySmall, big: Big):
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


def H_drop_typing_prefix(a: Any, b: List, c: Union[Any, List]):
    pass


def I_union_from_typing(a: Union[int, str, Union[list, tuple]]):
    pass


def J_union_from_typing_with_default(a: Union[int, str, Union[list, tuple]] = None):
    pass


def K_nested(a: List[int],
             b: List[Union[int, float]],
             c: Tuple[Tuple[UnknownType], Dict[str, Tuple[float]]]):
    pass


def L_iteral(a: Literal['on', 'off', 'int'],
              b: Literal[1, 2, 3],
              c: Literal[Small.one, True, None]):
    pass


try:
    exec('''
def M_union_syntax(a: int | str | list | tuple):
    pass


def N_union_syntax_with_default(a: int | str | list | tuple = None):
    pass
''')
except TypeError:    # Python < 3.10
    pass
