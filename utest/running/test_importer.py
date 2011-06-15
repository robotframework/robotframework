import unittest

from robot.running.importer import ImportCache
from robot.utils.asserts import *


class TestLibraryCache(unittest.TestCase):

    def setUp(self):
        self.cache = ImportCache()
        self.cache[('lib', ['a1', 'a2'])] = 'Library'
        self.cache['res'] = 'Resource'

    def test_add_library(self):
        assert_equals(self.cache._keys, [['lib', ['a1', 'a2']], 'res'])
        assert_equals(self.cache._items, ['Library', 'Resource'])

    def test_get_existing_library(self):
        assert_equals(self.cache['res'], 'Resource')
        assert_equals(self.cache[('lib', ['a1', 'a2'])], 'Library')
        assert_equals(self.cache[('lib', ['a1', 'a2'])], 'Library')
        assert_equals(self.cache['res'], 'Resource')

    def test_get_non_existing_library(self):
        assert_raises(KeyError, self.cache.__getitem__, 'nonex')
        assert_raises(KeyError, self.cache.__getitem__, ('lib1', ['wrong']))

    def test_has_library(self):
        assert_true(('lib', ['a1', 'a2']) in self.cache)
        assert_false(('lib', ['a1', 'a2', 'wrong']) in self.cache)
        assert_false('nonex' in self.cache)


if __name__ == '__main__':
    unittest.main()
