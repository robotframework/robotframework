def list_(argument: list[int], expected=None):
    _validate_type(argument, expected)


def tuple_(argument: tuple[int, bool, float], expected=None):
    _validate_type(argument, expected)


def homogenous_tuple(argument: tuple[int, ...], expected=None):
    _validate_type(argument, expected)


def dict_(argument: dict[int, float], expected=None):
    _validate_type(argument, expected)


def set_(argument: set[bool], expected=None):
    _validate_type(argument, expected)


def invalid_list(a: list[int, float]):
    pass


def invalid_tuple(a: tuple[int, float, ...]):
    pass


def invalid_dict(a: dict[int]):
    pass


def invalid_set(a: set[int, float]):
    pass


def _validate_type(argument, expected):
    if isinstance(expected, str):
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        atype = type(argument).__name__
        etype = type(expected).__name__
        raise AssertionError(f'{argument!r} ({atype}) != {expected!r} ({etype})')
