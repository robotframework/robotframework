import unittest

from array import array
from collections import UserDict, UserList, UserString
from collections.abc import Mapping
from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Union

from robot.utils import (is_bytes, is_falsy, is_dict_like, is_list_like, is_string,
                         is_truthy, is_union, PY_VERSION, type_name, type_repr)
from robot.utils.asserts import assert_equal, assert_true


class MyMapping(Mapping):

    def __getitem__(self, item):
        return 0

    def __len__(self):
        return 0

    def __iter__(self):
        return iter([])


def generator():
    yield 'generated'


class TestIsMisc(unittest.TestCase):

    def test_strings(self):
        for thing in ['string', 'hyvä', '']:
            assert_equal(is_string(thing), True, thing)
            assert_equal(is_bytes(thing), False, thing)

    def test_bytes(self):
        for thing in [b'bytes', bytearray(b'ba'), b'', bytearray()]:
            assert_equal(is_bytes(thing), True, thing)
            assert_equal(is_string(thing), False, thing)

    def test_is_union(self):
        assert is_union(Union[int, str])
        assert not is_union((int, str))
        if PY_VERSION >= (3, 10):
            assert is_union(eval('int | str'))
        for not_union in 'string', 3, [int, str], list, List[int]:
            assert not is_union(not_union)


class TestListLike(unittest.TestCase):

    def test_strings_are_not_list_like(self):
        for thing in ['string', UserString('user')]:
            assert_equal(is_list_like(thing), False, thing)

    def test_bytes_are_not_list_like(self):
        for thing in [b'bytes', bytearray(b'bytes')]:
            assert_equal(is_list_like(thing), False, thing)

    def test_dict_likes_are_list_like(self):
        for thing in [dict(), UserDict(), MyMapping()]:
            assert_equal(is_list_like(thing), True, thing)

    def test_files_are_not_list_like(self):
        with open(__file__) as f:
            assert_equal(is_list_like(f), False)
        assert_equal(is_list_like(f), False)

    def test_iter_makes_object_iterable_regardless_implementation(self):
        class Example:
            def __iter__(self):
                1/0
        assert_equal(is_list_like(Example()), True)

    def test_only_getitem_does_not_make_object_iterable(self):
        class Example:
            def __getitem__(self, item):
                return "I'm not iterable!"
        assert_equal(is_list_like(Example()), False)

    def test_iterables_in_general_are_list_like(self):
        for thing in [[], (), set(), range(1), generator(), array('i'), UserList()]:
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
        for thing in ['', b'', 1, None, True, object(), [], (), set()]:
            assert_equal(is_dict_like(thing), False, thing)


class TestTypeName(unittest.TestCase):

    def test_base_types(self):
        for item, exp in [('x', 'string'),
                          (b'x', 'bytes'),
                          (bytearray(), 'bytearray'),
                          (1, 'integer'),
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
        class CamelCase: pass
        class lower: pass
        for item, exp in [(CamelCase(), 'CamelCase'),
                          (lower(), 'lower'),
                          (CamelCase, 'CamelCase')]:
            assert_equal(type_name(item), exp)

    def test_strip_underscores(self):
        class _Foo_: pass
        assert_equal(type_name(_Foo_), 'Foo')

    def test_none_as_underscore_name(self):
        class C:
            _name = None
        assert_equal(type_name(C()), 'C')
        assert_equal(type_name(C(), capitalize=True), 'C')

    def test_typing(self):
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
                          (Literal, 'Literal'),
                          (Literal['x', 1], 'Literal'),
                          (Any, 'Any')]:
            assert_equal(type_name(item), exp)

    if PY_VERSION >= (3, 10):
        def test_union_syntax(self):
            assert_equal(type_name(int | float), 'Union')

    def test_capitalize(self):
        class lowerclass: pass
        class CamelClass: pass
        assert_equal(type_name('string', capitalize=True), 'String')
        assert_equal(type_name(None, capitalize=True), 'None')
        assert_equal(type_name(lowerclass(), capitalize=True), 'Lowerclass')
        assert_equal(type_name(CamelClass(), capitalize=True), 'CamelClass')


class TestTypeRepr(unittest.TestCase):

    def test_class(self):
        class Foo:
            pass
        assert_equal(type_repr(Foo), 'Foo')

    def test_none(self):
        assert_equal(type_repr(None), 'None')

    def test_ellipsis(self):
        assert_equal(type_repr(...), '...')

    def test_string(self):
        assert_equal(type_repr('MyType'), 'MyType')

    def test_no_typing_prefix(self):
        assert_equal(type_repr(List), 'List')

    def test_generics_from_typing(self):
        assert_equal(type_repr(List[Any]), 'List[Any]')
        assert_equal(type_repr(Dict[int, None]), 'Dict[int, None]')
        assert_equal(type_repr(Tuple[int, ...]), 'Tuple[int, ...]')

    if PY_VERSION >= (3, 9):
        def test_generics(self):
            assert_equal(type_repr(list[Any]), 'list[Any]')
            assert_equal(type_repr(dict[int, None]), 'dict[int, None]')

    def test_union(self):
        assert_equal(type_repr(Union[int, float]), 'int | float')
        assert_equal(type_repr(Union[int, None, List[Any]]), 'int | None | List[Any]')
        assert_equal(type_repr(Union), 'Union')
        if PY_VERSION >= (3, 10):
            assert_equal(type_repr(int | None | list[Any]), 'int | None | list[Any]')

    def test_literal(self):
        assert_equal(type_repr(Literal['x', 1, True]), "Literal['x', 1, True]")
        assert_equal(type_repr(Literal['x', 1, True], nested=False), "Literal")


class TestIsTruthyFalsy(unittest.TestCase):

    def test_truthy_values(self):
        for item in [True, 1, [False], unittest.TestCase, 'truE', 'whatEver']:
            for item in self._strings_also_in_different_cases(item):
                assert_true(is_truthy(item) is True)
                assert_true(is_falsy(item) is False)

    def test_falsy_values(self):
        class AlwaysFalse:
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
