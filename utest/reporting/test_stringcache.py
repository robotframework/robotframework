import time
import random
import string
import unittest

from robot.reporting.stringcache import StringCache, StringIndex
from robot.utils.asserts import assert_equal, assert_true, assert_false


try:
    long
except NameError:
    long = int


class TestStringCache(unittest.TestCase):

    def setUp(self):
        # To make test reproducable log the random seed if test fails
        self._seed = long(time.time() * 256)
        random.seed(self._seed)
        self.cache = StringCache()

    def _verify_text(self, string, expected):
        self.cache.add(string)
        assert_equal(('*', expected), self.cache.dump())

    def _compress(self, text):
        return self.cache._encode(text)

    def test_short_test_is_not_compressed(self):
        self._verify_text('short', '*short')

    def test_long_test_is_compressed(self):
        long_string = 'long'*1000
        self._verify_text(long_string, self._compress(long_string))

    def test_coded_string_is_at_most_1_characters_longer_than_raw(self):
        for i in range(300):
            id = self.cache.add(self._generate_random_string(i))
            assert_true(i+1 >= len(self.cache.dump()[id]),
                        'len(self._text_cache.dump()[id]) (%s) > i+1 (%s) [test seed = %s]'
                        % (len(self.cache.dump()[id]), i+1, self._seed))

    def test_long_random_strings_are_compressed(self):
        for i in range(30):
            value = self._generate_random_string(300)
            id = self.cache.add(value)
            assert_equal(self._compress(value), self.cache.dump()[id],
                          msg='Did not compress [test seed = %s]' % self._seed)

    def _generate_random_string(self, length):
        return ''.join(random.choice(string.digits) for _ in range(length))

    def test_indices_reused_instances(self):
        strings = ['', 'short', 'long'*1000, '']
        indices1 = [self.cache.add(s) for s in strings]
        indices2 = [self.cache.add(s) for s in strings]
        for i1, i2 in zip(indices1, indices2):
            assert_true(i1 is i2, 'not same: %s and %s' % (i1, i2))


class TestStringIndex(unittest.TestCase):

    def test_to_string(self):
        value = StringIndex(42)
        assert_equal(str(value), '42')

    def test_truth(self):
        assert_true(StringIndex(1))
        assert_true(StringIndex(-42))
        assert_false(StringIndex(0))


if __name__ == '__main__':
    unittest.main()
