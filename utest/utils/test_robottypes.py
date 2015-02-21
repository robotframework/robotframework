import unittest

from collections import Mapping
from array import array
from UserDict import UserDict
from UserList import UserList
from UserString import UserString, MutableString
try:
    import java
    from java.lang import String
    from java.util import HashMap, Hashtable
except ImportError:
    pass

from robot.utils import (is_dict_like, is_list_like, is_str_like, type_name,
                         JYTHON)
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


class TestListLike(unittest.TestCase):

    def test_strings_are_not_list_like(self):
        for thing in ['str', u'unicode', UserString('user')]:
            assert_equals(is_list_like(thing), False, thing)

    def test_dict_likes_are_list_like(self):
        for thing in [dict(), UserDict(), MyMapping()]:
            assert_equals(is_list_like(thing), True, thing)

    if JYTHON:

        def test_java_strings_are_not_list_like(self):
            assert_equals(is_list_like(String()), False)

        def test_java_dict_likes_are_list_like(self):
            assert_equals(is_list_like(HashMap()), True)
            assert_equals(is_list_like(Hashtable()), True)

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


class TestDictLike(unittest.TestCase):

    def test_dict_likes(self):
        for thing in [dict(), UserDict(), MyMapping()]:
            assert_equals(is_dict_like(thing), True, thing)

    def test_others(self):
        for thing in ['', u'', 1, None, True, object(), [], (), set()]:
            assert_equals(is_dict_like(thing), False, thing)

    if JYTHON:

        def test_java_maps(self):
            assert_equals(is_dict_like(HashMap()), True)
            assert_equals(is_dict_like(Hashtable()), True)


class TestStringLike(unittest.TestCase):

    def test_string_likes(self):
        for thing in ['', 'a', u'\xe4', UserString('us'), MutableString('ms')]:
            assert_equals(is_str_like(thing), True, thing)

    def test_others(self):
        for thing in [1, None, True, object(), [], (), {}]:
            assert_equals(is_str_like(thing), False, thing)

    if JYTHON:

        def test_java_string(self):
            assert_equals(is_str_like(String()), True)
            assert_equals(is_str_like(String('xxx')), True)


class TestTypeName(unittest.TestCase):

    def test_base_types(self):
        for item, exp in [('bytes', 'string'), (u'unicode', 'string'),
                          (1, 'integer'), (1L, 'integer'), (1.0, 'float'),
                          (True, 'boolean'), (None, 'None'), (set(), 'set'),
                          ([], 'list'), ((), 'tuple'), ({}, 'dictionary')]:
            assert_equals(type_name(item), exp)

    def test_custom_objects(self):
        class NewStyle(object): pass
        class OldStyle: pass
        for item, exp in [(NewStyle(), 'NewStyle'), (OldStyle(), 'OldStyle'),
                          (NewStyle, 'type'), (OldStyle, 'classobj')]:
            assert_equals(type_name(item), exp)

    if JYTHON:

        def test_java_object(self):
            for item, exp in [(String(), 'String'), (String, 'Class'),
                              (java.lang, 'javapackage'), (java, 'javapackage')]:
                assert_equals(type_name(item), exp)


if __name__ == '__main__':
    unittest.main()
