import unittest

from collections import Mapping
from array import array
try :
    from UserDict import UserDict
    from UserList import UserList
    from UserString import UserString
except ImportError:
    from collections import UserDict, UserList, UserString

try:
    import java
    from java.lang import String
    from java.util import HashMap, Hashtable
except ImportError:
    pass

from robot.utils import is_dict_like, is_list_like, long, type_name, JYTHON
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

    def test_files_are_not_list_like(self):
        with open(__file__) as f:
            assert_equals(is_list_like(f), False)
        assert_equals(is_list_like(f), False)

    def test_object_raising_exception_are_not_list_like(self):
        class O(object):
            def __iter__(self):
                1/0
        assert_equals(is_list_like(O()), False)

    def test_other_iterables_are_list_like(self):
        try:
            xrange
        except NameError:
            xrange = range
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


class TestTypeName(unittest.TestCase):

    def test_base_types(self):
        for item, exp in [('bytes', 'string'), (u'unicode', 'string'),
                          (1, 'integer'), (long(1), 'integer'), (1.0, 'float'),
                          (True, 'boolean'), (None, 'None'), (set(), 'set'),
                          ([], 'list'), ((), 'tuple'), ({}, 'dictionary')]:
            assert_equals(type_name(item), exp)

    def test_file(self):
        with open(__file__) as f:
            assert_equals(type_name(f), 'file')

    def test_custom_objects(self):
        class NewStyle(object): pass
        class OldStyle: pass
        for item, exp in [(NewStyle(), 'NewStyle'), (OldStyle(), 'OldStyle'),
                          (NewStyle, 'class'), (OldStyle, 'class')]:
            assert_equals(type_name(item), exp)

    if JYTHON:

        def test_java_object(self):
            for item, exp in [(String(), 'String'), (String, 'Class'),
                              (java.lang, 'javapackage'), (java, 'javapackage')]:
                assert_equals(type_name(item), exp)


if __name__ == '__main__':
    unittest.main()
