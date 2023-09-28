def parameterized_list(argument: 'list[int]', expected=None):
    assert argument == eval(expected), repr(argument)


def parameterized_dict(argument: 'dict[int, float]', expected=None):
    assert argument == eval(expected), repr(argument)


def parameterized_set(argument: 'set[float]', expected=None):
    assert argument == eval(expected), repr(argument)


def parameterized_tuple(argument: 'tuple[int,float,     str   ]', expected=None):
    assert argument == eval(expected), repr(argument)


def homogenous_tuple(argument: 'tuple[int, ...]', expected=None):
    assert argument == eval(expected), repr(argument)


def union(argument: 'int | float', expected=None):
    assert argument == eval(expected), repr(argument)


def nested(argument: 'dict[int|float, tuple[int, ...] | tuple[int, float]]', expected=None):
    assert argument == eval(expected), repr(argument)


def invalid(argument: 'bad[info'):
    assert False
