import unittest
from robot.utils.asserts import assert_equal, assert_raises_with_msg

from robot.utils.setter import setter, SetterAwareType


class Example(object):
    @setter
    def attr(self, value):
        return value * 2

class ExampleWithSlots(object):
    __slots__ = []
    __metaclass__ = SetterAwareType
    @setter
    def attr(self, value):
        return value * 2


class TestSetter(unittest.TestCase):

    def setUp(self):
        self.item = Example()

    def test_setting(self):
        self.item.attr = 1
        assert_equal(self.item.attr, 2)

    def test_notset(self):
        assert_raises_with_msg(AttributeError, 'attr',
                               getattr, self.item, 'attr')


class TestSetterAwareType(TestSetter):

    def setUp(self):
        self.item = ExampleWithSlots()


if __name__ == '__main__':
    unittest.main()
