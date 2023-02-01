from enum import Enum

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # python < 3.8
from typing_extensions import Literal as ExtLiteral


class MyEnum(Enum):
    a = 1


def literal_of_all_types(argument: Literal[1, True, MyEnum.a, 'b', None, b'd'], expected,
                         enum=False):
    assert argument == (eval(expected) if enum else expected)


def invalid_literal(_argument: Literal[1.1]):
    pass


def literal_string_is_not_an_alias(argument: Literal['int']):
    pass


L = Literal[Literal[1], ExtLiteral[2]]


def nested_literal(argument: Literal[L]):
    ...


def external_literal(argument: ExtLiteral[L]):
    ...
