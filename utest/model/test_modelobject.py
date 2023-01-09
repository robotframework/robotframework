import re
import unittest

from robot.model.modelobject import ModelObject
from robot.utils.asserts import assert_equal, assert_raises


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


class TestFromDictAndJson(unittest.TestCase):

    def test_init_args(self):
        class X(ModelObject):
            def __init__(self, a=1, b=2):
                self.a = a
                self.b = b
        x = X.from_dict({'a': 3})
        assert_equal(x.a, 3)
        assert_equal(x.b, 2)
        x = X.from_json('{"a": "A", "b": true}')
        assert_equal(x.a, 'A')
        assert_equal(x.b, True)

    def test_other_attributes(self):
        class X(ModelObject):
            pass
        x = X.from_dict({'a': 1})
        assert_equal(x.a, 1)
        x = X.from_json('{"a": null, "b": 42}')
        assert_equal(x.a, None)
        assert_equal(x.b, 42)

    def test_not_accepted_attribute(self):
        class X(ModelObject):
            __slots__ = ['a']
        assert_equal(X.from_dict({'a': 1}).a, 1)
        err = assert_raises(ValueError, X.from_dict, {'b': 'bad'})
        expected = (f"Creating '{__name__}.X' object from dictionary failed: .*\n"
                    f"Dictionary:\n{{'b': 'bad'}}")
        if not re.fullmatch(expected, str(err)):
            raise AssertionError(f'Unexpected error message. Expected:\n{expected}\n\n'
                                 f'Actual:\n{err}')


if __name__ == '__main__':
    unittest.main()
