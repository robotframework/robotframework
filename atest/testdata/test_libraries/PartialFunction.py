from functools import partial


def function(value, expected, lower=False):
    if lower is True:
        value = value.lower()
    assert value == expected


partial_function = partial(function, expected='value')
