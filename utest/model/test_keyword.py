import unittest
from robot.utils.asserts import assert_equal, assert_true, assert_raises

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

    def test_slots(self):
        assert_raises(AttributeError, setattr, Keyword(), 'attr', 'value')


class TestStringRepresentation(unittest.TestCase):

    def setUp(self):
        self.empty = Keyword()
        self.ascii = Keyword(name='Kekkonen')
        self.non_ascii = Keyword(name=u'hyv\xe4 nimi')

    def test_unicode(self):
        assert_equal(unicode(self.empty), '')
        assert_equal(unicode(self.ascii), 'Kekkonen')
        assert_equal(unicode(self.non_ascii), u'hyv\xe4 nimi')

    def test_str(self):
        assert_equal(str(self.empty), '')
        assert_equal(str(self.ascii), 'Kekkonen')
        assert_equal(str(self.non_ascii), 'hyv? nimi')

    def test_repr(self):
        assert_equal(repr(self.empty), "''")
        assert_equal(repr(self.ascii), "'Kekkonen'")
        assert_equal(repr(self.non_ascii), "'hyv? nimi'")


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
