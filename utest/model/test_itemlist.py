from six import text_type as unicode

import unittest
from robot.utils.asserts import assert_equal, assert_true, assert_raises_with_msg

from robot.model.itemlist import ItemList


class Object(object):
    attr = 1

class OldStyle:
    pass

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
        class Item(object):
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

    def test_only_matching_types_can_be_added(self):
        assert_raises_with_msg(TypeError,
                               'Only int objects accepted, got str.',
                               ItemList(int).append, 'not integer')
        assert_raises_with_msg(TypeError,
                               'Only OldStyle objects accepted, got Object.',
                               ItemList(OldStyle).append, Object())
        assert_raises_with_msg(TypeError,
                               'Only Object objects accepted, got OldStyle.',
                               ItemList(Object).append, OldStyle())

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

    def test_getitem_slice_is_not_supported(self):
        assert_raises_with_msg(TypeError,
                               'ItemList instances do not support slicing.',
                               ItemList(int).__getitem__, slice(0))
        assert_raises_with_msg(TypeError,
                               'CustomItems instances do not support slicing.',
                               CustomItems(int).__getitem__, slice(0))
    def test_index(self):
        items = ItemList(str, items=('first', 'second'))
        assert_equal(items.index('first'), 0)
        assert_equal(items.index('second'), 1)

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

    def test_setitem_slice_is_not_supported(self):
        assert_raises_with_msg(TypeError,
                               'ItemList instances do not support slicing.',
                               ItemList(int).__setitem__, slice(0), [])
        assert_raises_with_msg(TypeError,
                               'CustomItems instances do not support slicing.',
                               CustomItems(int).__setitem__, slice(0), [])

    def test_len(self):
        items = ItemList(object)
        assert_equal(len(items), 0)
        items.create()
        assert_equal(len(items), 1)

    def test_truth(self):
        assert_true(not ItemList(int))
        assert_true(ItemList(int, items=[1]))

    def test_clear(self):
        items = ItemList(int, items=list(range(10)))
        items.clear()
        assert_equal(len(items), 0)

    def test_str(self):
        assert_equal(str(ItemList(str, items=['foo', 'bar', 'quux'])),
                     '[foo, bar, quux]')

    def test_unicode(self):
        assert_equal(unicode(ItemList(int, items=[1, 2, 3, 4])),
                     '[1, 2, 3, 4]')
        assert_equal(unicode(ItemList(unicode, items=[u'hyv\xe4\xe4', u'y\xf6'])),
                     u'[hyv\xe4\xe4, y\xf6]')


if __name__ == '__main__':
    unittest.main()
