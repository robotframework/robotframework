import time
import random
import string
import unittest
from sys import maxint

from robot.reporting.parsingcontext import Context, TextCache, TextIndex
from robot.result import TestSuite, Message
from robot.utils.asserts import assert_equals, assert_true, assert_raises


class TestTextContext(unittest.TestCase):

    def setUp(self):
        self._context = Context()

    def _verify_ids(self, values, ids):
        results = []
        for value in values:
            results.append(self._context.get_id(value))
        assert_equals(ids, results)


    def _verify_text(self, values, ids, dump):
        self._verify_ids(values, ids)
        assert_equals(self._context.dump_texts(), dump)

    def test_add_empty_string(self):
        self._verify_text([''], [0] , ['*'])

    def test_add_text(self):
        self._verify_text(['Hello!'], [1] , ['*', '*Hello!'])

    def test_add_several_texts(self):
        self._verify_text(['Hello!', '', 'Foo'], [1, 0, 2] , ['*', '*Hello!', '*Foo'])


class TestTextCache(unittest.TestCase):

    def setUp(self):
        # To make test reproducable log the random seed if test fails
        self._seed = long(time.time() * 256)
        random.seed(self._seed)
        self._text_cache = TextCache()

    def _verify_text(self, string, expected):
        self._text_cache.add(string)
        assert_equals(['*', expected], self._text_cache.dump())

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


class TestSplittingContext(unittest.TestCase):

    def setUp(self):
        self._context = Context(split_log=True)

    def test_getting_split_results(self):
        assert_equals(self._context.split_results, [])

    def test_keyword_data_for_single_test(self):
        self._context.start_test()
        self._context.start_keyword()
        self._context.end_keyword()
        test_index = self._context.end_test(['my kw data'])
        assert_equals(self._context.split_results, [(['my kw data'], ['*'])])
        assert_equals(test_index, 1)

    def test_adding_strings_for_single_keyword(self):
        self._context.start_test()
        self._context.start_keyword()
        self._context.get_id('log message')
        self._context.end_keyword()
        self._context.end_test(['data'])
        assert_equals(self._context.split_results, [(['data'], ['*', '*log message'])])

    def test_adding_strings_before_keyword(self):
        self._context.start_test()
        self._context.get_id('log message')
        self._context.start_keyword()
        self._context.end_keyword()
        self._context.end_test(['data'])
        assert_equals(self._context.split_results, [(['data'], ['*'])])

    def test_recursive_keywords(self):
        self._context.start_test()
        self._context.start_keyword()
        self._context.start_keyword()
        self._context.end_keyword()
        self._context.end_keyword()
        self._context.end_test(['my kw data'])
        assert_equals(self._context.split_results, [(['my kw data'], ['*'])])

    def test_several_keywords(self):
        self._context.start_test()
        self._context.start_keyword()
        self._context.end_keyword()
        self._context.start_keyword()
        self._context.end_keyword()
        self._context.end_test(['kw data 1', 'kw data 2'])
        assert_equals(self._context.split_results, [(['kw data 1', 'kw data 2'], ['*'])])

    def test_several_tests(self):
        self._context.start_test()
        self._context.start_keyword()
        self._context.end_keyword()
        test_index1 = self._context.end_test(['kw data 1'])
        self._context.start_test()
        self._context.start_keyword()
        self._context.end_keyword()
        test_index2 = self._context.end_test(['kw data 2'])
        assert_equals(self._context.split_results, [(['kw data 1'], ['*']),
                                                    (['kw data 2'], ['*'])])
        assert_equals(test_index1, 1)
        assert_equals(test_index2, 2)

    def test_several_tests_texts(self):
        self._context.start_test()
        self._context.start_keyword()
        self._context.get_id('log message in test 1')
        self._context.end_keyword()
        self._context.end_test(['kw data 1'])
        self._context.start_test()
        self._context.start_keyword()
        self._context.get_id('log message in test 2')
        self._context.end_keyword()
        self._context.end_test(['kw data 2'])
        assert_equals(self._context.split_results, [(['kw data 1'], ['*', '*log message in test 1']),
                                                    (['kw data 2'], ['*', '*log message in test 2'])])


class TestTextIndex(unittest.TestCase):

    def test_to_string(self):
        value = TextIndex(42)
        assert_equals(str(value), '42')

    def test_long_values(self):
        target = maxint + 42
        value = TextIndex(target)
        assert_equals(str(value), str(target))


class TestTimestamp(unittest.TestCase):

    def setUp(self):
        self._context = Context()

    def test_timestamp(self):
        assert_equals(self._context.timestamp('20110603 12:00:00.042'), 0)
        assert_equals(self._context.timestamp('20110603 12:00:00.043'), 1)
        assert_equals(self._context.timestamp('20110603 12:00:00.000'), -42)
        assert_equals(self._context.timestamp('20110603 12:00:01.041'), 999)

    def test_na_timestamp(self):
        assert_equals(self._context.timestamp('N/A'), None)


class TestLinking(unittest.TestCase):

    def test_suite_keyword(self):
        self._verify_link(TestSuite(), 's1')
        self._verify_link(TestSuite().suites.create(), 's1-s1')

    def test_test_keyword(self):
        self._verify_link(TestSuite().tests.create(), 's1-t1')

    def test_sub_keyword(self):
        test = TestSuite().suites.create().tests.create()
        test.keywords.create()
        test.keywords.create()
        kw = test.keywords.create().keywords.create().keywords.create()
        self._verify_link(kw, 's1-s1-t1-k3-k1-k1')

    def _verify_link(self, parent, expected):
        msg1 = Message(message='msg', timestamp='xxx', parent=parent)
        msg2 = Message(message='msg', timestamp='xxx', parent=parent)
        msg3 = Message(message='msg', timestamp='yyy', parent=parent)
        ctx = Context()
        ctx.create_link_to_current_location(msg1)
        assert_equals(ctx.link_to(msg1), expected)
        assert_equals(ctx.link_to(msg2), expected)
        assert_raises(KeyError, ctx.link_to, msg3)


if __name__ == '__main__':
    unittest.main()
