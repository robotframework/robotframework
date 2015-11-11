import unittest
import os
import pkgutil

from robot.running import namespace
from robot import libraries
from robot.utils.asserts import assert_equal


class TestNamespace(unittest.TestCase):

    def test_standard_library_names(self):
        module_path = os.path.dirname(libraries.__file__)
        exp_libs = (name for _, name, _ in pkgutil.iter_modules([module_path])
                    if name[0].isupper() and not name.startswith('Deprecated'))
        assert_equal(set(exp_libs), namespace.STDLIBS)
