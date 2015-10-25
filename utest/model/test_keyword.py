import unittest
from robot.utils.asserts import assert_equal, assert_true, assert_raises

from robot.model import TestSuite, Message
from robot.model.keyword import Keyword, Keywords
from robot.utils import PY2, PY3


if PY3:
    unicode = str


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


class TestChildren(unittest.TestCase):

    def test_only_keywords(self):
        kw = Keyword()
        for i in range(10):
            kw.keywords.create(str(i))
        assert_equal(kw.children, list(kw.keywords))

    def test_only_messages(self):
        kw = Keyword()
        for i in range(10):
            kw.messages.create(str(i))
        assert_equal(kw.children, list(kw.messages))

    def test_order(self):
        kw = Keyword()
        m1 = kw.messages.create('m1')
        k1 = kw.keywords.create('k1')
        k2 = kw.keywords.create('k2')
        m2 = kw.messages.create('m2')
        k3 = kw.keywords.create('k3')
        assert_equal(kw.children, [m1, k1, k2, m2, k3])

    def test_order_after_modifications(self):
        kw = Keyword()
        kw.keywords.create('k1')
        kw.messages.create('m1')
        k2 = kw.keywords.create('k2')
        m2 = kw.messages.create('m2')
        k1 = kw.keywords[0] = Keyword('k1-new')
        m1 = kw.messages[0] = Message('m1-new')
        m3 = Message('m3')
        kw.messages.append(m3)
        k3 = Keyword('k3')
        kw.keywords.extend([k3])
        assert_equal(kw.children, [k1, m1, k2, m2, m3, k3])
        kw.keywords = [k1, k3]
        kw.messages = [m1]
        assert_equal(kw.children, [k1, m1, k3])


class TestStringRepresentation(unittest.TestCase):

    def setUp(self):
        self.empty = Keyword()
        self.ascii = Keyword(name='Kekkonen')
        self.non_ascii = Keyword(name=u'hyv\xe4 nimi')

    def test_unicode(self):
        assert_equal(unicode(self.empty), '')
        assert_equal(unicode(self.ascii), 'Kekkonen')
        assert_equal(unicode(self.non_ascii), u'hyv\xe4 nimi')

    if PY2:
        def test_str(self):
            assert_equal(str(self.empty), '')
            assert_equal(str(self.ascii), 'Kekkonen')
            assert_equal(str(self.non_ascii), u'hyv\xe4 nimi'.encode('UTF-8'))


class TestKeywords(unittest.TestCase):

    def test_setup(self):
        assert_equal(Keywords().setup, None)
        setup = Keyword(type='setup')
        assert_true(Keywords(keywords=[setup, Keyword(), Keyword()]).setup is setup)

    def test_teardown(self):
        assert_equal(Keywords().teardown, None)
        teardown = Keyword(type='teardown')
        assert_true(Keywords(keywords=[Keyword(), teardown]).teardown is teardown)

    def test_for_loops_are_included(self):
        kws = [Keyword(type='for'), Keyword(), Keyword(type='foritem')]
        assert_equal(list(Keywords(keywords=kws).normal), kws)
        assert_equal(list(Keywords(keywords=kws).all), kws)

    def test_iteration(self):
        kws = [Keyword(type='setup'), Keyword(), Keyword(), Keyword(type='teardown')]
        assert_equal(list(Keywords(keywords=kws)), kws)
        assert_equal(list(Keywords(keywords=kws).all), kws)
        assert_equal(list(Keywords(keywords=kws).normal), kws[1:-1])


if __name__ == '__main__':
    unittest.main()
