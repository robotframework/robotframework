import sys
from typing import List, NoReturn, Union

if sys.version_info >= (3, 11):
    from typing import Never
else:
    from typing_extensions import Never

if sys.version_info >= (3, 12):
    exec("type TypeAlias = int")  # noqa: S102
else:
    TypeAlias = int


class Unknown:
    pass


def A_no_return_type():
    pass


def B_none_return() -> None:
    pass


def C_simple_return() -> int:
    return 42


def D_parameterized_return() -> List[int]:
    return []


def E_union_return() -> Union[int, float]:
    return 42


def F_stringified_return() -> "int | float":
    return 42


def G_unknown_return() -> Unknown:
    return Unknown()


def H_invalid_return() -> "list[int":  # noqa: F722
    pass


def I_Never() -> Never:
    raise AssertionError


def J_NoReturn() -> NoReturn:
    raise AssertionError


def K_type_alias() -> TypeAlias:
    return 42
