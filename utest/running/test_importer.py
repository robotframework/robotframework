import unittest
import os
from os.path import abspath, join

from robot.running.importer import ImportCache
from robot.errors import FrameworkError
from robot.utils.asserts import assert_equal, assert_true, assert_raises
from robot.utils import normpath


class TestImportCache(unittest.TestCase):

    def setUp(self):
        self.cache = ImportCache()
        self.cache[('lib', ['a1', 'a2'])] = 'Library'
        self.cache['res'] = 'Resource'

    def test_add_item(self):
        assert_equal(self.cache._keys, [('lib', ['a1', 'a2']), 'res'])
        assert_equal(self.cache._items, ['Library', 'Resource'])

    def test_overwrite_item(self):
        self.cache['res'] = 'New Resource'
        assert_equal(self.cache['res'], 'New Resource')
        assert_equal(self.cache._keys, [('lib', ['a1', 'a2']), 'res'])
        assert_equal(self.cache._items, ['Library', 'New Resource'])

    def test_get_existing_item(self):
        assert_equal(self.cache['res'], 'Resource')
        assert_equal(self.cache[('lib', ['a1', 'a2'])], 'Library')
        assert_equal(self.cache[('lib', ['a1', 'a2'])], 'Library')
        assert_equal(self.cache['res'], 'Resource')

    def test_contains_item(self):
        assert_true(('lib', ['a1', 'a2']) in self.cache)
        assert_true('res' in self.cache)
        assert_true(('lib', ['a1', 'a2', 'wrong']) not in self.cache)
        assert_true('nonex' not in self.cache)

    def test_get_non_existing_item(self):
        assert_raises(KeyError, self.cache.__getitem__, 'nonex')
        assert_raises(KeyError, self.cache.__getitem__, ('lib1', ['wrong']))

    def test_invalid_key(self):
        assert_raises(FrameworkError, self.cache.__setitem__, ['inv'], None)

    def test_existing_absolute_paths_are_normalized(self):
        cache = ImportCache()
        path = join(abspath('.'), '.', os.listdir('.')[0])
        value = object()
        cache[path] = value
        assert_equal(cache[path], value)
        assert_equal(cache._keys[0], normpath(path, case_normalize=True))

    def test_existing_non_absolute_paths_are_not_normalized(self):
        cache = ImportCache()
        path = os.listdir('.')[0]
        value = object()
        cache[path] = value
        assert_equal(cache[path], value)
        assert_equal(cache._keys[0], path)

    def test_non_existing_absolute_paths_are_not_normalized(self):
        cache = ImportCache()
        path = join(abspath('.'), '.', 'NonExisting.file')
        value = object()
        cache[path] = value
        assert_equal(cache[path], value)
        assert_equal(cache._keys[0], path)


if __name__ == '__main__':
    unittest.main()
