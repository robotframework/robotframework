import unittest

from robot.model.modelobject import ModelObject
from robot.utils.asserts import assert_equal


class TestRepr(unittest.TestCase):

    def test_default(self):
        assert_equal(repr(ModelObject()), 'robot.model.ModelObject()')

    def test_module_when_extending(self):
        class X(ModelObject):
            pass
        assert_equal(repr(X()), '%s.X()' % __name__)

    def test_repr_args(self):
        class X(ModelObject):
            repr_args = ('z', 'x')
            x, y, z = 1, 2, 3
        assert_equal(repr(X()), '%s.X(z=3, x=1)' % __name__)


if __name__ == '__main__':
    unittest.main()
