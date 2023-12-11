import unittest

from robot.running import ResourceFile, UserKeyword
from robot.utils.asserts import assert_equal, assert_not_equal


class TestCacheInvalidation(unittest.TestCase):

    def setUp(self):
        self.resource = ResourceFile()
        self.keywords = self.resource.keywords
        self.keywords.create(name='A', doc='a')
        self.b = UserKeyword(name='B', doc='b')
        self.exists('A')
        self.doesnt('B')

    def exists(self, name):
        kw, = self.resource.find_keywords(name)
        assert_equal(kw.doc, name.lower())

    def doesnt(self, name):
        kws = self.resource.find_keywords(name)
        assert_equal(len(kws), 0)

    def test_recreate_cache(self):
        self.resource.keyword_finder.invalidate_cache()
        assert_equal(self.resource.keyword_finder.cache, None)
        self.exists('A')
        assert_not_equal(self.resource.keyword_finder.cache, None)

    def test_create(self):
        self.keywords.create(name='B', doc='b')
        self.exists('B')

    def test_append(self):
        self.keywords.append(self.b)
        self.exists('B')

    def test_extend(self):
        self.keywords.extend([self.b])
        self.exists('B')

    def test_setitem(self):
        self.keywords[0] = self.b
        self.exists('B')
        self.doesnt('A')

    def test_insert(self):
        self.keywords.insert(0, self.b)
        self.exists('B')
        self.exists('A')

    def test_clear(self):
        self.keywords.clear()
        self.doesnt('A')

    def test_assign(self):
        self.resource.keywords = [self.b]
        self.exists('B')
        self.doesnt('A')
        self.resource.keywords = []
        self.doesnt('B')

    def test_change_keyword_name(self):
        self.keywords[0].config(name='X', doc='x')
        self.exists('X')
        self.doesnt('A')


if __name__ == '__main__':
    unittest.main()
