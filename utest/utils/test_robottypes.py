import unittest

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
from array import array
try:
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

from robot.utils import (is_bytes, is_falsy, is_dict_like, is_list_like,
                         is_string, is_truthy, type_name, IRONPYTHON, JYTHON,
                         PY3)
from robot.utils.asserts import assert_equal, assert_true


if PY3:
    long = int
    xrange = range


class MyMapping(Mapping):

    def __getitem__(self, item):
        return 0

    def __len__(self):
        return 0

    def __iter__(self):
        return iter([])


def generator():
    yield 'generated'


class TestStringsAndBytes(unittest.TestCase):

    def test_strings(self):
        for thing in ['string', u'unicode', '', u'']:
            assert_equal(is_string(thing), True, thing)
            assert_equal(is_bytes(thing), isinstance(thing, bytes), thing)

    def test_bytes(self):
        for thing in [b'bytes', bytearray(b'ba'), b'', bytearray()]:
            assert_equal(is_bytes(thing), True, thing)
            assert_equal(is_string(thing), isinstance(thing, str), thing)


class TestListLike(unittest.TestCase):

    def test_strings_are_not_list_like(self):
        for thing in ['str', u'unicode', UserString('user')]:
            assert_equal(is_list_like(thing), False, thing)

    def test_bytes_are_not_list_like(self):
        for thing in [b'bytes', bytearray(b'bytes')]:
            assert_equal(is_list_like(thing), False, thing)

    def test_dict_likes_are_list_like(self):
        for thing in [dict(), UserDict(), MyMapping()]:
            assert_equal(is_list_like(thing), True, thing)

    if JYTHON:

        def test_java_strings_are_not_list_like(self):
            assert_equal(is_list_like(String()), False)

        def test_java_dict_likes_are_list_like(self):
            assert_equal(is_list_like(HashMap()), True)
            assert_equal(is_list_like(Hashtable()), True)

    def test_files_are_not_list_like(self):
        with open(__file__) as f:
            assert_equal(is_list_like(f), False)
        assert_equal(is_list_like(f), False)

    def test_iter_makes_object_iterable_regardless_implementation(self):
        class Example(object):
            def __iter__(self):
                1/0
        assert_equal(is_list_like(Example()), True)

    def test_only_getitem_does_not_make_object_iterable(self):
        class Example(object):
            def __getitem__(self, item):
                return "I'm not iterable!"
        assert_equal(is_list_like(Example()), False)

    def test_iterables_in_general_are_list_like(self):
        for thing in [[], (), set(), xrange(1), generator(), array('i'), UserList()]:
            assert_equal(is_list_like(thing), True, thing)

    def test_others_are_not_list_like(self):
        for thing in [1, None, True, object()]:
            assert_equal(is_list_like(thing), False, thing)

    def test_generators_are_not_consumed(self):
        g = generator()
        assert_equal(is_list_like(g), True)
        assert_equal(is_list_like(g), True)
        assert_equal(list(g), ['generated'])
        assert_equal(list(g), [])
        assert_equal(is_list_like(g), True)


class TestDictLike(unittest.TestCase):

    def test_dict_likes(self):
        for thing in [dict(), UserDict(), MyMapping()]:
            assert_equal(is_dict_like(thing), True, thing)

    def test_others(self):
        for thing in ['', u'', 1, None, True, object(), [], (), set()]:
            assert_equal(is_dict_like(thing), False, thing)

    if JYTHON:

        def test_java_maps(self):
            assert_equal(is_dict_like(HashMap()), True)
            assert_equal(is_dict_like(Hashtable()), True)


class TestTypeName(unittest.TestCase):

    def test_base_types(self):
        for item, exp in [('x', 'string'),
                          (u'x', 'string'),
                          (b'x', 'bytes' if (PY3 or IRONPYTHON) else 'string'),
                          (bytearray(), 'bytearray'),
                          (1, 'integer'),
                          (long(1), 'integer'),
                          (1.0, 'float'),
                          (True, 'boolean'),
                          (None, 'None'),
                          (set(), 'set'),
                          ([], 'list'),
                          ((), 'tuple'),
                          ({}, 'dictionary')]:
            assert_equal(type_name(item), exp)

    def test_file(self):
        with open(__file__) as f:
            assert_equal(type_name(f), 'file')

    def test_custom_objects(self):
        class NewStyle(object): pass
        class OldStyle: pass
        class lower: pass
        for item, exp in [(NewStyle(), 'NewStyle'),
                          (OldStyle(), 'OldStyle'),
                          (lower(), 'lower'),
                          (NewStyle, 'NewStyle'),
                          (OldStyle, 'OldStyle')]:
            assert_equal(type_name(item), exp)

    def test_strip_underscores(self):
        class _Foo_(object): pass
        assert_equal(type_name(_Foo_), 'Foo')

    def test_none_as_underscore_name(self):
        class C(object):
            _name = None
        assert_equal(type_name(C()), 'C')
        assert_equal(type_name(C(), capitalize=True), 'C')

    if PY3:

        def test_typing(self):
            from typing import Any, Dict, List, Optional, Set, Tuple, Union

            for item, exp in [(List, 'list'),
                              (List[int], 'list'),
                              (Tuple, 'tuple'),
                              (Tuple[int], 'tuple'),
                              (Set, 'set'),
                              (Set[int], 'set'),
                              (Dict, 'dictionary'),
                              (Dict[int, str], 'dictionary'),
                              (Union, 'Union'),
                              (Union[int, str], 'Union'),
                              (Optional, 'Optional'),
                              (Optional[int], 'Union'),
                              (Any, 'Any')]:
                assert_equal(type_name(item), exp)

    if JYTHON:

        def test_java_object(self):
            for item, exp in [(String(), 'String'),
                              (String, 'String'),
                              (java.lang, 'javapackage'),
                              (java, 'javapackage')]:
                assert_equal(type_name(item), exp)

    def test_capitalize(self):
        class lowerclass: pass
        class CamelClass: pass
        assert_equal(type_name('string', capitalize=True), 'String')
        assert_equal(type_name(None, capitalize=True), 'None')
        assert_equal(type_name(lowerclass(), capitalize=True), 'Lowerclass')
        assert_equal(type_name(CamelClass(), capitalize=True), 'CamelClass')


class TestIsTruthyFalsy(unittest.TestCase):

    def test_truthy_values(self):
        for item in [True, 1, [False], unittest.TestCase, 'truE', 'whatEver']:
            for item in self._strings_also_in_different_cases(item):
                assert_true(is_truthy(item) is True)
                assert_true(is_falsy(item) is False)

    def test_falsy_values(self):
        class AlwaysFalse(object):
            __bool__ = __nonzero__ = lambda self: False
        falsy_strings = ['', 'faLse', 'nO', 'nOne', 'oFF', '0']
        for item in falsy_strings + [False, None, 0, [], {}, AlwaysFalse()]:
            for item in self._strings_also_in_different_cases(item):
                assert_true(is_truthy(item) is False)
                assert_true(is_falsy(item) is True)

    def _strings_also_in_different_cases(self, item):
        yield item
        if is_string(item):
            yield item.lower()
            yield item.upper()
            yield item.title()


if __name__ == '__main__':
    unittest.main()
