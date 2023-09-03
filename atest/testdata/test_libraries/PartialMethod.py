from functools import partialmethod


class PartialMethod:

    def method(self, value, expected, lower: bool = False):
        if lower is True:
            value = value.lower()
        assert value == expected

    partial_method = partialmethod(method, expected='value')
