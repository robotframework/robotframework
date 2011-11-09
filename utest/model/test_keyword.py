import unittest
from robot.utils.asserts import assert_equal, assert_true

from robot.model import TestSuite
from robot.model.keyword import Keyword, Keywords


class TestKeyword(unittest.TestCase):

    def test_id_without_parent(self):
        assert_equal(Keyword().id, 'k1')

    def test_id_with_suite_parent(self):
        assert_equal(TestSuite().keywords.create().id, 's1-k1')

    def test_id_with_test_parent(self):
        assert_equal(TestSuite().tests.create().keywords.create().id, 's1-t1-k1')

    def test_id_with_keyword_parents(self):
        kw = TestSuite().tests.create().keywords.create()
        kw.keywords = [Keyword(), Keyword()]
        kw.keywords[-1].keywords.create()
        assert_equal(kw.keywords[0].id, 's1-t1-k1-k1')
        assert_equal(kw.keywords[1].id, 's1-t1-k1-k2')
        assert_equal(kw.keywords[1].keywords[0].id, 's1-t1-k1-k2-k1')


class TestKeywords(unittest.TestCase):

    def test_setup(self):
        assert_equal(Keywords().setup, None)
        setup = Keyword(type='setup')
        assert_true(Keywords(items=[setup, Keyword(), Keyword()]).setup is setup)

    def test_teardown(self):
        assert_equal(Keywords().teardown, None)
        teardown = Keyword(type='teardown')
        assert_true(Keywords(items=[Keyword(), teardown]).teardown is teardown)

    def test_for_loops_are_included(self):
        kws = [Keyword(type='for'), Keyword(), Keyword(type='foritem')]
        assert_equal(list(Keywords(items=kws).normal), kws)
        assert_equal(list(Keywords(items=kws).all), kws)

    def test_iteration(self):
        kws = [Keyword(type='setup'), Keyword(), Keyword(), Keyword(type='teardown')]
        assert_equal(list(Keywords(items=kws)), kws)
        assert_equal(list(Keywords(items=kws).all), kws)
        assert_equal(list(Keywords(items=kws).normal), kws[1:-1])


if __name__ == '__main__':
    unittest.main()
