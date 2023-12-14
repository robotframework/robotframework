import unittest

from robot.running import ResourceFile, UserKeyword
from robot.utils.asserts import assert_equal, assert_not_equal, assert_raises_with_msg


class TestResourceFile(unittest.TestCase):

    def setUp(self):
        self.resource = ResourceFile()
        for name in 'A', '${x:x}yz', 'x${y}z':
            self.resource.keywords.create(name)

    def find(self, name, count=None):
        return self.resource.find_keywords(name, count)

    def should_find(self, name, *matches, count=None):
        kws = self.find(name, count)
        assert_equal([k.name for k in kws], list(matches))

    def test_find_normal_keywords(self):
        self.should_find('A', 'A')
        self.should_find('a', 'A')
        self.should_find('B')

    def test_find_keywords_with_embedded_args(self):
        self.should_find('xxz', 'x${y}z')
        self.should_find('XZZ', 'x${y}z')
        self.should_find('XYZ', '${x:x}yz', 'x${y}z')

    def test_find_with_count(self):
        assert_equal(self.find('A', 1).name, 'A')
        assert_equal(len(self.find('B', 0)), 0)
        assert_equal(len(self.find('xyz', 2)), 2)

    def test_find_with_invalid_count(self):
        assert_raises_with_msg(
            ValueError,
            "Expected 2 keywords matching name 'A', found 1: 'A'",
            self.find, 'A', 2
        )
        assert_raises_with_msg(
            ValueError,
            "Expected 1 keyword matching name 'B', found 0.",
            self.find, 'B', 1
        )
        assert_raises_with_msg(
            ValueError,
            "Expected 1 keyword matching name 'xyz', found 2: '${x:x}yz' and 'x${y}z'",
            self.find, 'xyz', 1
        )


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
