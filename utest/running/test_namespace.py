import unittest
import os
import pkgutil

from robot.running import namespace
from robot import libraries
from robot.utils.asserts import assert_equals

class TestNamespace(unittest.TestCase):

    def test_standard_library_names(self):
        module_path = os.path.dirname(libraries.__file__)
        exp_libs = [m[1] for m in pkgutil.iter_modules([module_path])
                    if not m[1].startswith('Deprecated')]
        assert_equals(exp_libs, namespace.STDLIB_NAMES)

