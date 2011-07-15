import time
import random
import string
import unittest
from sys import maxint

from robot.result.parsingcontext import Context, TextCache, Stats, Location, TextIndex
from robot.utils.asserts import assert_equals, assert_true


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
        self._context.start_suite()

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


class TestStats(unittest.TestCase):

    def setUp(self):
        self.s1 = Stats()
        self.s11 = self.s1.new_child()
        self.s12 = self.s1.new_child()
        self.s121 = self.s12.new_child()
        self.s1211 = self.s121.new_child()

    def _test(self, stats, all, all_passed, crit=None, crit_passed=None):
        if crit is None:
            crit, crit_passed = all, all_passed
        assert_equals(stats.all, all)
        assert_equals(stats.all_passed, all_passed)
        assert_equals(stats.critical, crit)
        assert_equals(stats.critical_passed, crit_passed)
        assert_equals(list(stats), [all, all_passed, crit, crit_passed])

    def test_add_test(self):
        self.s1.add_test(critical=True, passed=True)
        self._test(self.s1, 1, 1)
        self.s11.add_test(True, False)
        self._test(self.s1, 2, 1)
        self._test(self.s11, 1, 0)
        self.s1211.add_test(False, True)
        self._test(self.s1, 3, 2, 2, 1)
        self._test(self.s11, 1, 0)
        self._test(self.s12, 1, 1, 0, 0)
        self._test(self.s121, 1, 1, 0, 0)
        self._test(self.s1211, 1, 1, 0, 0)

    def test_teardown_failed(self):
        self.s1.add_test(critical=True, passed=True)
        self.s12.add_test(True, True)
        self.s121.add_test(True, True)
        self.s1211.add_test(False, True)
        self.s121.suite_teardown_failed()
        self._test(self.s1211, 1, 0, 0, 0)
        self._test(self.s121, 2, 0, 1, 0)
        self._test(self.s12, 3, 1, 2, 1)
        self._test(self.s1, 4, 2, 3, 2)

    def test_stats_through_context(self):
        context = Context()
        context.start_suite()
        context.start_suite()
        context.add_test(1,1)
        child_stats = context.end_suite()
        self.assertEqual(list(child_stats), [1, 1, 1, 1])
        context.suite_teardown_failed()
        parent_stats = context.end_suite()
        self.assertEqual(list(child_stats), [1, 0, 1, 0])
        self.assertEqual(list(parent_stats), [1, 0, 1, 0])


class TestLocation(unittest.TestCase):

    def setUp(self):
        self._loc = Location()
        self._loc.start_suite()

    def _verify_id(self, id):
        assert_equals(self._loc.current_id, id)

    def test_start_one_suite(self):
        self._verify_id('s1')

    def test_start_multiple_suites(self):
        self._loc.start_suite()
        self._loc.start_suite()
        self._verify_id('s1-s1-s1')

    def test_start_and_end_suites(self):
        self._loc.start_suite()
        self._loc.end_suite()
        self._verify_id('s1')
        self._loc.start_suite()
        self._verify_id('s1-s2')
        self._loc.end_suite()
        self._verify_id('s1')

    def test_start_test(self):
        self._loc.start_test()
        self._verify_id('s1-t1')

    def test_start_and_end_tests(self):
        self._loc.start_test()
        self._loc.end_test()
        self._loc.start_test()
        self._verify_id('s1-t2')
        self._loc.end_test()
        self._loc.start_suite()
        self._loc.start_test()
        self._verify_id('s1-s1-t1')
        self._loc.end_test()
        self._loc.end_suite()
        self._verify_id('s1')

    def test_keywords_in_test(self):
        self._loc.start_test()
        self._loc.start_keyword()
        self._loc.start_keyword()
        self._verify_id('s1-t1-k1-k1')
        self._loc.end_keyword()
        self._verify_id('s1-t1-k1')
        self._loc.start_keyword()
        self._verify_id('s1-t1-k1-k2')
        self._loc.end_keyword()
        self._verify_id('s1-t1-k1')
        self._loc.end_keyword()
        self._verify_id('s1-t1')
        self._loc.end_test()
        self._verify_id('s1')

    def test_suite_setup_and_teardown(self):
        self._loc.start_keyword()
        self._verify_id('s1-k1')
        self._loc.end_keyword()
        self._loc.start_test()
        self._loc.start_keyword()
        self._verify_id('s1-t1-k1')
        self._loc.end_keyword()
        self._loc.end_test()
        self._loc.start_keyword()
        self._verify_id('s1-k2')
        self._loc.end_keyword()
        self._loc.start_suite()
        self._loc.start_keyword()
        self._verify_id('s1-s1-k1')
        self._loc.end_keyword()
        self._verify_id('s1-s1')


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

    def setUp(self):
        self._context = Context()

    def _kw(self, inner_func=None):
        self._context.start_keyword()
        if inner_func:
            inner_func(self._context)
        self._context.end_keyword()

    def test_link_creation(self):
        key = [4,'W',6]
        self._create_data_and_link(key)
        self.assertEqual(self._context.link_to(key), 's1-s1-t1-k1')

    def _create_data_and_link(self, key):
        self._context.start_suite()
        self._context.start_suite()
        self._context.start_test()
        self._context.start_keyword()
        self._context.create_link_to_current_location(key)
        self._context.end_keyword()
        self._context.end_test()
        self._context.end_suite()
        self._context.end_suite()

    def test_2_links(self):
        key1 = [1,'W',2]
        key2 = [2,'W',5]
        self._create_data_for_links(key1, key2)
        self.assertEqual(self._context.link_to(key1), 's1-k1')
        self.assertEqual(self._context.link_to(key2), 's1-t1-k1-k2')

    def _create_data_for_links(self, key1, key2):
        self._context.start_suite()
        self._kw(lambda ctx: ctx.create_link_to_current_location(key1))
        self._context.start_test()
        self._context.start_keyword()
        self._kw()
        self._kw(lambda ctx: ctx.create_link_to_current_location(key2))
        self._context.end_keyword()
        self._context.end_test()
        self._context.end_suite()

    def test_link_to_subkeyword(self):
        key = [1, 'W', 542]
        self._create_data_for_subkeyword(key)
        self.assertEqual(self._context.link_to(key), 's1-t1-k3-k2')

    def _create_data_for_subkeyword(self, key):
        self._context.start_suite()
        self._context.start_test()
        self._kw()
        self._kw()
        self._context.start_keyword()
        self._kw()
        self._context.start_keyword()
        self._context.create_link_to_current_location(key)
        self._kw()
        self._kw()
        self._context.end_keyword()
        self._context.end_test()
        self._context.end_suite()

    def test_link_to_suite_teardown(self):
        pkey = [5, 'W', 321]
        skey = [4, 'W', 3214]
        self._create_data_for_suite_teardown_links(pkey, skey)
        self.assertEqual(self._context.link_to(skey),'s1-s1-k1')
        self.assertEqual(self._context.link_to(pkey), 's1-k2')

    def _create_data_for_suite_teardown_links(self, pkey, skey):
        self._context.start_suite()
        self._kw()
        self._context.start_suite()
        self._context.start_test()
        self._kw()
        self._context.end_test()
        self._kw(lambda ctx: ctx.create_link_to_current_location(skey))
        self._context.end_suite()
        self._kw(lambda ctx: ctx.create_link_to_current_location(pkey))
        self._context.end_suite()

        
if __name__ == '__main__':
    unittest.main()
