import unittest
import sys

try:
    from collections import Mapping
except ImportError:
    Mapping = dict
try:
    from java.lang import String
    from java.util import HashMap
except ImportError:
    pass
from array import array
from UserDict import UserDict
from UserList import UserList
from UserString import UserString, MutableString

from robot.utils import is_dict_like, is_list_like, is_str_like
from robot.utils.asserts import assert_equals


class MyMapping(Mapping):

    def __getitem__(self, item):
        return 0

    def __len__(self):
        return 0

    def __iter__(self):
        return iter([])


def generator():
    yield 'generated'


class TestListlike(unittest.TestCase):

    def test_strings_are_not_list_like(self):
        for thing in ['str', u'unicode', UserString('user')]:
            assert_equals(is_list_like(thing), False, thing)

    def test_dict_likes_are_not_list_like(self):
        for thing in [dict(), UserDict(), MyMapping()]:
            assert_equals(is_list_like(thing), False, thing)

    if sys.platform.startswith('java'):

        def test_java_strings_are_not_list_like(self):
            assert_equals(is_list_like(String()), False)

        def test_java_dict_likes_are_not_list_like(self):
            assert_equals(is_list_like(HashMap()), False)

    def test_other_iterables_are_list_like(self):
        for thing in [[], (), set(), xrange(1), generator(), array('i'), UserList()]:
            assert_equals(is_list_like(thing), True, thing)

    def test_others_are_not_list_like(self):
        for thing in [1, None, True, object()]:
            assert_equals(is_list_like(thing), False, thing)

    def test_generators_are_not_consumed(self):
        g = generator()
        assert_equals(is_list_like(g), True)
        assert_equals(is_list_like(g), True)
        assert_equals(list(g), ['generated'])
        assert_equals(list(g), [])
        assert_equals(is_list_like(g), True)


class TestDictlike(unittest.TestCase):

    def test_dict_likes(self):
        for thing in [dict(), UserDict(), MyMapping()]:
            assert_equals(is_dict_like(thing), True, thing)

    def test_others(self):
        for thing in ['', u'', 1, None, True, object(), [], (), set()]:
            assert_equals(is_dict_like(thing), False, thing)

    def test_allow_java(self):
        assert_equals(is_dict_like({}, allow_java=True), True)
        assert_equals(is_dict_like([], allow_java=True), False)
        if sys.platform.startswith('java'):
            assert_equals(is_dict_like(HashMap()), False)
            assert_equals(is_dict_like(HashMap(), allow_java=True), True)
            assert_equals(is_dict_like([], allow_java=True), False)


class TestStringlike(unittest.TestCase):

    def test_string_likes(self):
        for thing in ['', 'a', u'\xe4', UserString('us'), MutableString('ms')]:
            assert_equals(is_str_like(thing), True, thing)

    def test_others(self):
        for thing in [1, None, True, object(), [], (), {}]:
            assert_equals(is_str_like(thing), False, thing)

    def test_allow_java(self):
        assert_equals(is_str_like('', allow_java=True), True)
        assert_equals(is_str_like([], allow_java=True), False)
        if sys.platform.startswith('java'):
            assert_equals(is_str_like(String()), False)
            assert_equals(is_str_like(String(), allow_java=True), True)
            assert_equals(is_str_like([], allow_java=True), False)


if __name__ == "__main__":
    unittest.main()
