import unittest
import os
import pkgutil

from robot.running import namespace
from robot.running.namespace import _VariableScopes, GLOBAL_VARIABLES
from robot import libraries
from robot.utils.asserts import assert_equals


class TestNamespace(unittest.TestCase):

    def test_standard_library_names(self):
        module_path = os.path.dirname(libraries.__file__)
        exp_libs = (name for _, name, _ in pkgutil.iter_modules([module_path])
                    if name[0].isupper() and not name.startswith('Deprecated'))
        assert_equals(set(exp_libs), namespace.STDLIB_NAMES)


class TestVariableScopes(unittest.TestCase):

    def test_len(self):
        variables = {'foo': 'bar', 'quuz': 'blaah'}
        assert_equals(len(_VariableScopes(None, None)), 0)
        assert_equals(len(_VariableScopes(variables, None)), 2 + len(GLOBAL_VARIABLES))
        assert_equals(len(_VariableScopes(None, _VariableScopes(variables, None))), 0)
