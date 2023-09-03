import unittest
from robot.utils.asserts import (assert_equal, assert_false, assert_true,
                                 assert_raises, assert_raises_with_msg)

from robot.model.itemlist import ItemList


class Object:
    attr = 1

    def __init__(self, id=None):
        self.id = id

    def __eq__(self, other):
        return isinstance(other, Object) and self.id == other.id


class CustomItems(ItemList):
    pass


class TestItemLists(unittest.TestCase):

    def test_create_items(self):
        items = ItemList(str)
        item = items.create(object=1)
        assert_true(isinstance(item, str))
        assert_equal(item, '1')
        assert_equal(list(items), [item])

    def test_create_with_args_and_kwargs(self):
        class Item:
            def __init__(self, arg1, arg2):
                self.arg1 = arg1
                self.arg2 = arg2
        items = ItemList(Item)
        item = items.create('value 1', arg2='value 2')
        assert_equal(item.arg1, 'value 1')
        assert_equal(item.arg2, 'value 2')
        assert_equal(list(items), [item])

    def test_append_and_extend(self):
        items = ItemList(int)
        items.append(1)
        items.append(2)
        items.extend((3, 4))
        assert_equal(list(items), [1, 2, 3, 4])

    def test_extend_with_generator(self):
        items = ItemList(str)
        items.extend((c for c in 'Hello, world!'))
        assert_equal(list(items), list('Hello, world!'))

    def test_insert(self):
        items = ItemList(str)
        items.insert(0, 'a')
        items.insert(0, 'b')
        items.insert(3, 'c')
        items.insert(1, 'd')
        assert_equal(list(items), ['b', 'd', 'a', 'c'])

    def test_only_matching_types_can_be_added(self):
        assert_raises_with_msg(TypeError,
                               'Only integer objects accepted, got string.',
                               ItemList(int).append, 'not integer')
        assert_raises_with_msg(TypeError,
                               'Only integer objects accepted, got Object.',
                               ItemList(int).extend, [Object()])
        assert_raises_with_msg(TypeError,
                               'Only Object objects accepted, got integer.',
                               ItemList(Object).insert, 0, 42)

    def test_initial_items(self):
        assert_equal(list(ItemList(Object, items=[])), [])
        assert_equal(list(ItemList(int, items=(1, 2, 3))), [1, 2, 3])

    def test_common_attrs(self):
        item1 = Object()
        item2 = Object()
        parent = object()
        items = ItemList(Object, {'attr': 2, 'parent': parent}, [item1])
        items.append(item2)
        assert_true(item1.parent is parent)
        assert_equal(item1.attr, 2)
        assert_true(item2.parent is parent)
        assert_equal(item2.attr, 2)
        assert_equal(list(items), [item1, item2])

    def test_getitem(self):
        item1 = object()
        item2 = object()
        items = ItemList(object, items=[item1, item2])
        assert_true(items[0] is item1)
        assert_true(items[1] is item2)
        assert_true(items[-1] is item2)

    def test_getitem_slice(self):
        items = ItemList(int, items=range(10))
        sub = items[:5]
        assert_true(isinstance(sub, ItemList))
        assert_equal(list(sub), list(range(5)))
        assert_equal(list(items), list(range(10)))
        sub.append(5)
        assert_equal(list(sub), list(range(6)))
        assert_equal(list(items), list(range(10)))
        backwards = items[::-1]
        assert_true(isinstance(backwards, ItemList))
        assert_equal(list(backwards), list(reversed(items)))
        empty = items[100:]
        assert_true(isinstance(empty, ItemList))
        assert_equal(list(empty), [])

    def test_index(self):
        items = ItemList(str, items=('first', 'second'))
        assert_equal(items.index('first'), 0)
        assert_equal(items.index('second'), 1)
        assert_raises(ValueError, items.index, 'nonex')

    def test_index_with_start_and_stop(self):
        numbers = [0, 1, 2, 3, 2, 1, 0]
        items = ItemList(int, items=numbers)
        for num in sorted(set(numbers)):
            for start in range(len(numbers)):
                if num in numbers[start:]:
                    assert_equal(items.index(num, start),
                                 numbers.index(num, start))
                    for end in range(start, len(numbers)):
                        if num in numbers[start:end]:
                            assert_equal(items.index(num, start, end),
                                         numbers.index(num, start, end))

    def test_setitem(self):
        orig1, orig2 = Object(), Object()
        new1, new2 = Object(), Object()
        items = ItemList(Object, {'attr': 2}, [orig1, orig2])
        items[0] = new1
        assert_equal(list(items), [new1, orig2])
        assert_equal(new1.attr, 2)
        items[-1] = new2
        assert_equal(list(items), [new1, new2])
        assert_equal(new2.attr, 2)

    def test_setitem_slice(self):
        items = ItemList(int, items=range(10))
        items[:5] = []
        items[-2:] = [42]
        assert_equal(list(items), [5, 6, 7, 42])
        items = CustomItems(Object, {'a': 1}, [Object(i) for i in range(10)])
        items[1::3] = tuple(Object(c) for c in 'abc')
        assert_true(all(obj.a == 1 for obj in items))
        assert_equal([obj.id for obj in items],
                     [0, 'a', 2, 3, 'b', 5, 6, 'c', 8, 9])

    def test_setitem_slice_invalid_type(self):
        assert_raises_with_msg(TypeError,
                               'Only integer objects accepted, got float.',
                               ItemList(int).__setitem__, slice(0), [1, 1.1])

    def test_delitem(self):
        items = ItemList(str, items='abcde')
        del items[0]
        assert_equal(list(items), list('bcde'))
        del items[1]
        assert_equal(list(items), list('bde'))
        del items[-1]
        assert_equal(list(items), list('bd'))
        assert_raises(IndexError, items.__delitem__, 10)
        assert_equal(list(items), list('bd'))

    def test_delitem_slice(self):
        items = ItemList(str, items='abcde')
        del items[1:3]
        assert_equal(list(items), list('ade'))
        del items[2:]
        assert_equal(list(items), list('ad'))
        del items[10:]
        assert_equal(list(items), list('ad'))
        del items[:]
        assert_equal(list(items), [])

    def test_pop(self):
        items = ItemList(str, items='abcde')
        assert_equal(items.pop(), 'e')
        assert_equal(items.pop(0), 'a')
        assert_equal(items.pop(-2), 'c')
        assert_equal(list(items), ['b', 'd'])
        assert_raises(IndexError, items.pop, 7)
        assert_equal(list(items), ['b', 'd'])
        assert_raises(IndexError, ItemList(int).pop)

    def test_remove(self):
        items = ItemList(str, items='abcba')
        items.remove('c')
        assert_equal(list(items), list('abba'))
        items.remove('a')
        assert_equal(list(items), list('bba'))
        items.remove('b')
        items.remove('a')
        items.remove('b')
        assert_equal(list(items), list(''))
        assert_raises(ValueError, items.remove, 'nonex')

    def test_len(self):
        items = ItemList(object)
        assert_equal(len(items), 0)
        items.create()
        assert_equal(len(items), 1)

    def test_truth(self):
        assert_true(not ItemList(int))
        assert_true(ItemList(int, items=[1]))

    def test_contains(self):
        items = ItemList(str, items='x')
        assert_true('x' in items)
        assert_true('y' not in items)
        assert_false('x' not in items)
        assert_false('y' in items)

    def test_clear(self):
        items = ItemList(int, items=range(10))
        assert_equal(len(items), 10)
        items.clear()
        assert_equal(len(items), 0)

    def test_str(self):
        assert_equal(str(ItemList(int, items=[1, 2, 3, 4])), '[1, 2, 3, 4]')
        assert_equal(str(ItemList(str, items=['foo', 'bar'])), "['foo', 'bar']")
        assert_equal(str(ItemList(int, items=[1, 2, 3, 4])), '[1, 2, 3, 4]')
        assert_equal(str(ItemList(str, items=['hyvää', 'yötä'])), "['hyvää', 'yötä']")

    def test_repr(self):
        assert_equal(repr(ItemList(int, items=[1, 2, 3, 4])),
                     'ItemList(item_class=int, items=[1, 2, 3, 4])')
        assert_equal(repr(CustomItems(Object)),
                     'CustomItems(item_class=Object, items=[])')

    def test_iter(self):
        numbers = list(range(10))
        items = ItemList(int, items=numbers)
        assert_equal(list(items), numbers)
        assert_equal(tuple(items), tuple(numbers))
        for i, n in zip(items, numbers):
            assert_equal(i, n)

    def test_modifications_during_iter(self):
        chars = ItemList(str, items='abdx')
        for c in chars:
            if c == 'a':
                chars.pop()
            if c == 'b':
                chars.insert(2, 'c')
            if c == 'c':
                chars.append('e')
            assert_true(c in 'abcde', '%s was unexpected here!' % c)
        assert_equal(list(chars), list('abcde'))

    def test_count(self):
        obj1 = object()
        obj2 = object()
        objects = ItemList(object, items=[obj1, obj2, object(), obj2])
        assert_equal(objects.count(obj1), 1)
        assert_equal(objects.count(obj2), 2)
        assert_equal(objects.count(object()), 0)
        assert_equal(objects.count('whatever'), 0)

    def test_sort(self):
        chars = ItemList(str, items='asDfG')
        chars.sort()
        assert_equal(list(chars), ['D', 'G', 'a', 'f', 's'])
        chars.sort(key=str.lower)
        assert_equal(list(chars), ['a', 'D', 'f', 'G', 's'])
        chars.sort(reverse=True)
        assert_equal(list(chars), ['s', 'f', 'a', 'G', 'D'])

    def test_sorted(self):
        chars = ItemList(str, items='asdfg')
        assert_equal(sorted(chars), sorted('asdfg'))

    def test_reverse(self):
        chars = ItemList(str, items='asdfg')
        chars.reverse()
        assert_equal(list(chars), list(reversed('asdfg')))

    def test_reversed(self):
        chars = ItemList(str, items='asdfg')
        assert_equal(list(reversed(chars)), list(reversed('asdfg')))

    def test_modifications_during_reversed(self):
        chars = ItemList(str, items='yxdba')
        for c in reversed(chars):
            if c == 'a':
                chars.remove('x')
            if c == 'b':
                chars.insert(-2, 'c')
            if c == 'c':
                chars.pop(0)
            if c == 'd':
                chars.insert(0, 'e')
            assert_true(c in 'abcde', '%s was unexpected here!' % c)
        assert_equal(list(chars), list('edcba'))

    def test_comparisons(self):
        n123 = ItemList(int, items=[1, 2, 3])
        n123b = ItemList(int, items=[1, 2, 3])
        n1234 = ItemList(int, items=[1, 2, 3, 4])
        n124 = ItemList(int, items=[1, 2, 4])
        assert_true(n123 == n123b)
        assert_false(n123 != n123b)
        assert_true(n123 != n1234)
        assert_false(n123 == n1234)
        assert_true(n1234 > n123)
        assert_true(n1234 >= n123)
        assert_false(n1234 < n123)
        assert_false(n1234 <= n123)
        assert_true(n124 > n123)
        assert_true(n124 >= n123)
        assert_false(n124 < n123)
        assert_false(n124 <= n123)
        assert_true(n123 >= n123)
        assert_true(n123 <= n123)

    def test_compare_incompatible(self):
        assert_false(ItemList(int) == ItemList(str))
        assert_false(ItemList(int) == ItemList(int, {'a': 1}))
        assert_raises_with_msg(TypeError, 'Cannot order incompatible ItemLists.',
                               ItemList(int).__gt__, ItemList(str))
        assert_raises_with_msg(TypeError, 'Cannot order incompatible ItemLists.',
                               ItemList(int).__gt__, ItemList(int, {'a': 1}))

    def test_comparisons_with_other_objects(self):
        items = ItemList(int, items=[1, 2, 3])
        assert_false(items == 123)
        assert_false(items == [1, 2, 3])
        assert_false(items == (1, 2, 3))
        assert_true(items != 123)
        assert_true(items != [1, 2, 3])
        assert_true(items != (1, 2, 3))
        assert_raises_with_msg(TypeError, 'Cannot order ItemList and integer.',
                               items.__gt__, 1)
        assert_raises_with_msg(TypeError, 'Cannot order ItemList and list.',
                               items.__lt__, [1, 2, 3])
        assert_raises_with_msg(TypeError, 'Cannot order ItemList and tuple.',
                               items.__ge__, (1, 2, 3))

    def test_add(self):
        assert_equal(ItemList(int, items=[1, 2]) + ItemList(int, items=[3, 4]),
                     ItemList(int, items=[1, 2, 3, 4]))

    def test_add_incompatible(self):
        assert_raises_with_msg(TypeError,
                               'Cannot add ItemList and list.',
                               ItemList(int).__add__, [])
        assert_raises_with_msg(TypeError,
                               'Cannot add incompatible ItemLists.',
                               ItemList(int).__add__, ItemList(str))
        assert_raises_with_msg(TypeError,
                               'Cannot add incompatible ItemLists.',
                               ItemList(int).__add__, ItemList(int, {'a': 1}))

    def test_iadd(self):
        items = ItemList(int, items=[1, 2])
        items += (3, 4)
        items += [5]
        items += (i for i in (6, 7))
        items += ItemList(int, items=[8, 9])
        items += ItemList(int)
        assert_equal(items, ItemList(int, items=[1, 2, 3, 4, 5, 6, 7, 8, 9]))

    def test_iadd_incompatible(self):
        items = ItemList(int, items=[1, 2])
        assert_raises_with_msg(TypeError, 'Cannot add incompatible ItemLists.',
                               items.__iadd__, ItemList(str))
        assert_raises_with_msg(TypeError, 'Cannot add incompatible ItemLists.',
                               items.__iadd__, ItemList(int, {'a': 1}))

    def test_iadd_wrong_type(self):
        assert_raises_with_msg(TypeError,
                               'Only integer objects accepted, got string.',
                               ItemList(int).__iadd__, ['a', 'b', 'c'])

    def test_mul(self):
        assert_equal(ItemList(int, items=[1, 2, 3]) * 2,
                     ItemList(int, items=[1, 2, 3, 1, 2, 3]))
        assert_raises(TypeError, ItemList(int).__mul__, ItemList(int))

    def test_imul(self):
        items = ItemList(int, items=[1, 2])
        items *= 2
        items *= 1
        assert_equal(items, ItemList(int, items=[1, 2, 1, 2]))

    def test_rmul(self):
        assert_equal(2 * ItemList(int, items=[1, 2, 3]),
                     ItemList(int, items=[1, 2, 3, 1, 2, 3]))
        assert_raises(TypeError, ItemList(int).__rmul__, ItemList(int))

    def test_items_as_dicts_without_from_dict(self):
        items = ItemList(Object, items=[{'id': 1}, {}])
        items.append({'id': 3})
        assert_equal(items[0].id, 1)
        assert_equal(items[1].id, None)
        assert_equal(items[2].id, 3)

    def test_items_as_dicts_with_from_dict(self):
        class ObjectWithFromDict(Object):
            @classmethod
            def from_dict(cls, data):
                obj = cls()
                for name in data:
                    setattr(obj, name, data[name])
                return obj

        items = ItemList(ObjectWithFromDict, items=[{'id': 1, 'attr': 2}])
        items.extend([{}, {'new': 3}])
        assert_equal(items[0].id, 1)
        assert_equal(items[0].attr, 2)
        assert_equal(items[1].id, None)
        assert_equal(items[1].attr, 1)
        assert_equal(items[2].new, 3)

    def test_to_dicts_without_to_dict(self):
        items = ItemList(Object, items=[Object(1), Object(2)])
        dicts = items.to_dicts()
        assert_equal(dicts, [{'id': 1}, {'id': 2}])
        assert_equal(ItemList(Object, items=dicts), items)

    def test_to_dicts_with_to_dict(self):
        class ObjectWithToDict(Object):
            def to_dict(self):
                return {'id': self.id, 'x': 42}

        items = ItemList(ObjectWithToDict, items=[ObjectWithToDict(1)])
        assert_equal(items.to_dicts(), [{'id': 1, 'x': 42}])


if __name__ == '__main__':
    unittest.main()
