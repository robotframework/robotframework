import time
import random
import string
import unittest
import sys

from robot.reporting.parsingcontext import TextCache, TextIndex
from robot.reporting.jsmodelbuilders import JsBuildingContext
from robot.result import TestSuite, Message
from robot.utils.asserts import assert_equals, assert_true, assert_false, assert_raises


class TestStringContext(unittest.TestCase):

    def test_add_empty_string(self):
        self._verify([''], [0] , ('*',))

    def test_add_text(self):
        self._verify(['Hello!'], [1] , ('*', '*Hello!'))

    def test_add_several_texts(self):
        self._verify(['Hello!', '', 'Foo'], [1, 0, 2] , ('*', '*Hello!', '*Foo'))

    def _verify(self, strings, exp_ids, exp_strings):
        ctx = JsBuildingContext()
        results = [ctx.string(s) for s in strings]
        assert_equals(results, exp_ids)
        assert_equals(ctx.strings, exp_strings)


class TestTextCache(unittest.TestCase):

    def setUp(self):
        # To make test reproducable log the random seed if test fails
        self._seed = long(time.time() * 256)
        random.seed(self._seed)
        self._text_cache = TextCache()

    def _verify_text(self, string, expected):
        self._text_cache.add(string)
        assert_equals(('*', expected), self._text_cache.dump())

    def _compress(self, text):
        return self._text_cache._compress(text)

    def test_short_test_is_not_compressed(self):
        self._verify_text('short', '*short')

    def test_long_test_is_compressed(self):
        long_string = 'long'*1000
        self._verify_text(long_string, self._compress(long_string))

    def test_coded_string_is_at_most_1_characters_longer_than_raw(self):
        for i in range(300):
            id = self._text_cache.add(self._generate_random_string(i))
            assert_true(i+1 >= len(self._text_cache.dump()[id]),
                        msg='len(self._text_cache.dump()[id]) (%s) > i+1 (%s) [test seed = %s]'  % \
                            (len(self._text_cache.dump()[id]), i+1, self._seed))

    def test_long_random_strings_are_compressed(self):
        for i in range(30):
            value = self._generate_random_string(300)
            id = self._text_cache.add(value)
            assert_equals(self._compress(value), self._text_cache.dump()[id],\
                          msg='Did not compress [test seed = %s]' % self._seed)

    def _generate_random_string(self, length):
        return ''.join(random.choice(string.digits) for _ in range(length))


class TestTextIndex(unittest.TestCase):

    def test_to_string(self):
        value = TextIndex(42)
        assert_equals(str(value), '42')

    def test_long_values(self):
        target = sys.maxint + 42
        value = TextIndex(target)
        assert_equals(str(value), str(target))
        assert_false(str(value).endswith('L'))


class TestTimestamp(unittest.TestCase):

    def setUp(self):
        self._context = JsBuildingContext()

    def test_timestamp(self):
        assert_equals(self._context.timestamp('20110603 12:00:00.042'), 0)
        assert_equals(self._context.timestamp('20110603 12:00:00.043'), 1)
        assert_equals(self._context.timestamp('20110603 12:00:00.000'), -42)
        assert_equals(self._context.timestamp('20110603 12:00:01.041'), 999)
        assert_equals(self._context.timestamp('20110604 12:00:00.042'),
                      24 * 60 * 60 * 1000)

    def test_na_timestamp(self):
        assert_equals(self._context.timestamp('N/A'), None)


if __name__ == '__main__':
    unittest.main()
