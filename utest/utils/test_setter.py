import unittest
from robot.utils.asserts import assert_equal, assert_raises

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
        assert_raises(AttributeError, getattr, self.item, 'attr')

    def test_set_other_attr(self):
        self.item.other_attr = 1
        assert_equal(self.item.other_attr, 1)


class TestSetterWithSlotsAndSetterAwareType(TestSetter):

    def setUp(self):
        self.item = ExampleWithSlots()

    def test_set_other_attr(self):
        assert_raises(AttributeError, setattr, self.item, 'other_attr', 1)


if __name__ == '__main__':
    unittest.main()
