import unittest

import robot.result.jsparser as jsparser

def _kw(context, inner_func=None):
    context.start_keyword()
    if inner_func: inner_func(context)
    context.end_keyword()

def _and(*funcs):
    def and_func(context):
        for func in funcs:
            func(context)
    return and_func


class TestParser(unittest.TestCase):

    def setUp(self):
        self._context = jsparser.Context()

    def test_timestamp(self):
        self.assertEqual(self._context.timestamp('20110603 12:00:00.000'), 0)
        self.assertEqual(self._context.timestamp('20110603 12:00:01.000'), 1000)

    def test_NA_timestamp(self):
        self.assertEqual(self._context.timestamp('N/A'), None)

    def test_stats_when_failing_suite_teardown(self):
        context = jsparser.Context()
        context.start_suite()
        context.start_suite()
        context.add_test(1,1)
        child_stats = context.end_suite()
        self.assertEqual(list(child_stats), [1, 1, 1, 1])
        context.suite_teardown_failed()
        parent_stats = context.end_suite()
        self.assertEqual(list(child_stats), [1, 0, 1, 0])
        self.assertEqual(list(parent_stats), [1, 0, 1, 0])

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
        _kw(self._context, lambda ctx: ctx.create_link_to_current_location(key1))
        self._context.start_test()
        self._context.start_keyword()
        _kw(self._context)
        _kw(self._context, lambda ctx: ctx.create_link_to_current_location(key2))
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
        _kw(self._context)
        _kw(self._context, _and(_kw, _kw, _kw))
        self._context.start_keyword()
        _kw(self._context)
        self._context.start_keyword()
        self._context.create_link_to_current_location(key)
        _kw(self._context)
        _kw(self._context)
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
        _kw(self._context) #Suite setup
        self._context.start_suite()
        self._context.start_test()
        _kw(self._context)
        self._context.end_test()
        _kw(self._context, lambda ctx: ctx.create_link_to_current_location(skey))
        self._context.end_suite()
        _kw(self._context, lambda ctx: ctx.create_link_to_current_location(pkey))
        self._context.end_suite()
