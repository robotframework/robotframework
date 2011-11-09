import unittest
from robot.utils.asserts import assert_equal, assert_true, assert_raises

from robot.model.itemlist import ItemList
from robot.model import Keyword


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
        assert_raises(TypeError, ItemList(int).append, 'not integer')

    def test_parent(self):
        kw1 = Keyword()
        kw2 = Keyword()
        parent = object()
        kws = ItemList(Keyword, [kw1], parent=parent)
        kws.append(kw2)
        assert_true(kw1.parent is parent)
        assert_true(kw2.parent is parent)
        assert_equal(list(kws), [kw1, kw2])

    def test_getitem(self):
        item1 = object()
        item2 = object()
        items = ItemList(object, [item1, item2])
        assert_true(items[0] is item1)
        assert_true(items[1] is item2)
        assert_true(items[-1] is item2)

    def test_getitem_slice_is_not_supported(self):
        assert_raises(ValueError, ItemList(int).__getitem__, slice(0))

    def test_len(self):
        items = ItemList(object)
        assert_equal(len(items), 0)
        items.create()
        assert_equal(len(items), 1)

    def test_str(self):
        items = ItemList(str, ['foo', 'bar', 'quux'])
        assert_equal(str(items), '[foo, bar, quux]')

    def test_unicode(self):
        assert_equal(unicode(ItemList(int, [1, 2, 3, 4])), '[1, 2, 3, 4]')
        assert_equal(unicode(ItemList(unicode, [u'hyv\xe4\xe4', u'y\xf6t\xe4'])),
                     u'[hyv\xe4\xe4, y\xf6t\xe4]')


if __name__ == '__main__':
    unittest.main()
