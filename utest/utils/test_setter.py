import unittest
from robot.utils.asserts import assert_equal, assert_raises

from robot.utils import setter, SetterAwareType


class ExampleWithSlots(metaclass=SetterAwareType):
    __slots__ = []

    @setter
    def attr(self, value):
        return value * 2

    @setter
    def with_doc(self, value):
        """The doc string."""
        return value


class Example(ExampleWithSlots):
    pass


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

    def test_copy_doc(self):
        assert_equal(type(self.item).attr.__doc__, None)
        assert_equal(type(self.item).with_doc.__doc__, "The doc string.")


class TestSetterWithSlotsAndSetterAwareType(TestSetter):

    def setUp(self):
        self.item = ExampleWithSlots()

    def test_set_other_attr(self):
        assert_raises(AttributeError, setattr, self.item, 'other_attr', 1)

    def test_slots_as_tuple(self):
        class XY(metaclass=SetterAwareType):
            __slots__ = ('x',)

            def __init__(self, x, y):
                self.x = x
                self.y = y

            @setter
            def y(self, y):
                return y.upper()

        xy = XY('x', 'y')
        assert_equal((xy.x, xy.y), ('x', 'Y'))
        assert_raises(AttributeError, setattr, xy, 'z', 'z')


if __name__ == '__main__':
    unittest.main()
