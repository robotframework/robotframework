from typing import List, Union


def A_no_return():
    pass


def B_none_return() -> None:
    pass


def C_simple_return() -> int:
    return 42


def D_parameterized_return() -> List[int]:
    return []


def E_union_return() -> Union[int, float]:
    return 42


def F_stringified_return() -> 'int | float':
    return 42


class Unknown:
    pass


def G_unknown_return() -> Unknown:
    return Unknown()


def H_invalid_return() -> 'list[int':
    pass
