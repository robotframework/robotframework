import unittest

from robot.api.deco import keyword
from robot.utils.asserts import assert_equals


class TestKeywordName(unittest.TestCase):

    def test_give_name_to_function(self):
        @keyword('Given name')
        def func():
            pass
        assert_equals(func.robot_name, 'Given name')

    def test_give_name_to_method(self):
        class Class:
            @keyword('Given name')
            def method(self):
                pass
        assert_equals(Class.method.robot_name, 'Given name')

    def test_no_name(self):
        @keyword()
        def func():
            pass
        assert_equals(func.robot_name, None)

    def test_no_name_nor_parens(self):
        @keyword
        def func():
            pass
        assert_equals(func.robot_name, None)
