import unittest

from robot.running.importer import _LibraryCache
from robot.utils.asserts import *


class TestLibraryCache(unittest.TestCase):

    def setUp(self):
        self.cache = _LibraryCache()
        self.cache[('lib', ['a1', 'a2'])] = 'Library'
        self.cache['res'] = 'Resource'
        
    def test_add_library(self):
        assert_equals(self.cache._keys, [('lib', ['a1', 'a2']), 'res'])
        assert_equals(self.cache._libs, ['Library', 'Resource'])

    def test_get_existing_library(self):
        assert_equals(self.cache['res'], 'Resource')
        assert_equals(self.cache[('lib', ['a1', 'a2'])], 'Library')        
        assert_equals(self.cache[('lib', ['a1', 'a2'])], 'Library')        
        assert_equals(self.cache['res'], 'Resource')

    def test_get_non_existing_library(self):
        assert_raises(KeyError, self.cache.__getitem__, 'nonex')
        assert_raises(KeyError, self.cache.__getitem__, ('lib1', ['wrong']))

    def test_has_library(self):
        assert_true(self.cache.has_key(('lib', ['a1', 'a2'])))
        assert_false(self.cache.has_key(('lib', ['a1', 'a2', 'wrong'])))
        assert_false(self.cache.has_key('nonex'))
        

if __name__ == '__main__':
    unittest.main()
