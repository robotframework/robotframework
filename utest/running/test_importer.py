import unittest

from robot.running.importer import ImportCache
from robot.errors import FrameworkError
from robot.utils.asserts import *


class TestImportCache(unittest.TestCase):

    def setUp(self):
        self.cache = ImportCache()
        self.cache[('lib', ['a1', 'a2'])] = 'Library'
        self.cache['res'] = 'Resource'

    def test_add_item(self):
        assert_equals(self.cache._keys, [('lib', ['a1', 'a2']), 'res'])
        assert_equals(self.cache._items, ['Library', 'Resource'])

    def test_overwrite_item(self):
        self.cache['res'] = 'New Resource'
        assert_equals(self.cache['res'], 'New Resource')
        assert_equals(self.cache._keys, [('lib', ['a1', 'a2']), 'res'])
        assert_equals(self.cache._items, ['Library', 'New Resource'])

    def test_get_existing_item(self):
        assert_equals(self.cache['res'], 'Resource')
        assert_equals(self.cache[('lib', ['a1', 'a2'])], 'Library')
        assert_equals(self.cache[('lib', ['a1', 'a2'])], 'Library')
        assert_equals(self.cache['res'], 'Resource')

    def test_contains_item(self):
        assert_true(('lib', ['a1', 'a2']) in self.cache)
        assert_true('res' in self.cache)
        assert_false(('lib', ['a1', 'a2', 'wrong']) in self.cache)
        assert_false('nonex' in self.cache)

    def test_get_non_existing_item(self):
        assert_raises(KeyError, self.cache.__getitem__, 'nonex')
        assert_raises(KeyError, self.cache.__getitem__, ('lib1', ['wrong']))

    def test_invalid_key(self):
        assert_raises(FrameworkError, self.cache.__setitem__, ['inv'], None)


if __name__ == '__main__':
    unittest.main()
