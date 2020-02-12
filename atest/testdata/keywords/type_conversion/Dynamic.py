from decimal import Decimal

from robot.api.deco import keyword
from robot.utils import unicode


class Dynamic(object):

    def get_keyword_names(self):
        return [name for name in dir(self)
                if hasattr(getattr(self, name), 'robot_name')]

    def run_keyword(self, name, args, kwargs):
        return getattr(self, name)(*args, **kwargs)

    def get_keyword_arguments(self, name):
        return ['value', 'expected=None']

    def get_keyword_types(self, name):
        return getattr(self, name).robot_types

    @keyword(types=[int])
    def list_of_types(self, value, expected=None):
        self._validate_type(value, expected)

    @keyword(types={'value': Decimal})
    def dict_of_types(self, value, expected=None):
        self._validate_type(value, expected)

    @keyword(types=['bytes'])
    def list_of_aliases(self, value, expected=None):
        self._validate_type(value, expected)

    @keyword(types={'value': 'Dictionary'})
    def dict_of_aliases(self, value, expected=None):
        self._validate_type(value, expected)

    def _validate_type(self, argument, expected):
        if isinstance(expected, unicode):
            expected = eval(expected)
        if argument != expected or type(argument) != type(expected):
            raise AssertionError('%r (%s) != %r (%s)'
                                 % (argument, type(argument).__name__,
                                    expected, type(expected).__name__))
