def integer(argument: int, expected=None):
    _validate_type(argument, expected)


def float_(argument: float, expected=None):
    _validate_type(argument, expected)


def boolean(argument: bool, expected=None):
    _validate_type(argument, expected)


def list_(argument: list, expected=None):
    _validate_type(argument, expected)


def tuple_(argument: tuple, expected=None):
    _validate_type(argument, expected)


def dictionary(argument: dict, expected=None):
    _validate_type(argument, expected)


def set_(argument: set, expected=None):
    _validate_type(argument, expected)


def _validate_type(argument, expected):
    if isinstance(expected, str) and not isinstance(argument, str):
        expected = eval(expected)
    if argument != expected or type(argument) != type(expected):
        raise AssertionError('%r != %r' % (argument, expected))
