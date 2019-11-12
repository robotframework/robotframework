import unittest
from robot.utils.asserts import (assert_equal, assert_none, assert_not_equal,
                                 assert_true, assert_raises, assert_raises_with_msg)

from robot.model import TestSuite, Message
from robot.model.keyword import Keyword, Keywords
from robot.utils import PY2, unicode


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

    def test_copy(self):
        kw = Keyword(name='Keyword')
        copy = kw.copy()
        assert_equal(kw.name, copy.name)
        copy.name += ' copy'
        assert_not_equal(kw.name, copy.name)
        assert_equal(id(kw.tags), id(copy.tags))

    def test_copy_with_attributes(self):
        kw = Keyword(name='Orig', doc='Orig', tags=['orig'])
        copy = kw.copy(name='New', doc='New', tags=['new'])
        assert_equal(copy.name, 'New')
        assert_equal(copy.doc, 'New')
        assert_equal(list(copy.tags), ['new'])

    def test_deepcopy(self):
        kw = Keyword(name='Keyword')
        copy = kw.deepcopy()
        assert_equal(kw.name, copy.name)
        assert_not_equal(id(kw.tags), id(copy.tags))

    def test_deepcopy_with_attributes(self):
        copy = Keyword(name='Orig').deepcopy(name='New', doc='New')
        assert_equal(copy.name, 'New')
        assert_equal(copy.doc, 'New')


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

    def test_get_setup(self):
        assert_none(Keywords().setup)
        setup = Keyword(type='setup')
        kws = Keywords(keywords=[setup, Keyword(), Keyword()])
        assert_true(kws.setup is setup)

    def test_set_setup(self):
        s1, s2, kw = Keyword(type='setup'), Keyword(type='setup'), Keyword()
        kws = Keywords(keywords=[kw])
        kws.setup = s1
        assert_true(kws.setup is s1)
        assert_equal(list(kws), [s1, kw])
        kws.setup = s2
        assert_true(kws.setup is s2)
        assert_equal(list(kws), [s2, kw])

    def test_setup_is_removed_when_set_to_none(self):
        kw = Keyword()
        kws = Keywords(keywords=[Keyword(type='setup'), kw])
        kws.setup = None
        assert_none(kws.setup)
        assert_equal(list(kws), [kw])
        kws.setup = None
        assert_none(kws.setup)
        assert_equal(list(kws), [kw])

    def test_setting_non_setup_keyword_to_setup_is_not_supported(self):

        kws = Keywords(keywords=[Keyword(type='setup'), Keyword(), Keyword()])
        orig = list(kws)
        assert_raises_with_msg(TypeError,
                               "Setup keyword type must be 'setup', got 'kw'.",
                               setattr, kws, 'setup', Keyword())
        assert_equal(list(kws), orig)

    def test_get_teardown(self):
        assert_equal(Keywords().teardown, None)
        teardown = Keyword(type='teardown')
        kws = Keywords(keywords=[Keyword(), teardown])
        assert_true(kws.teardown is teardown)

    def test_set_teardown(self):
        kw, t1, t2 = Keyword(), Keyword(type='teardown'), Keyword(type='teardown')
        kws = Keywords(keywords=[kw])
        kws.teardown = t1
        assert_true(kws.teardown is t1)
        assert_equal(list(kws), [kw, t1])
        kws.teardown = t2
        assert_true(kws.teardown is t2)
        assert_equal(list(kws), [kw, t2])

    def test_teardown_is_removed_when_set_to_none(self):
        kw = Keyword()
        kws = Keywords(keywords=[kw, Keyword(type='teardown')])
        kws.teardown = None
        assert_none(kws.teardown)
        assert_equal(list(kws), [kw])
        kws.teardown = None
        assert_none(kws.teardown)
        assert_equal(list(kws), [kw])

    def test_setting_non_teardown_keyword_to_teardown_is_not_supported(self):
        kws = Keywords(keywords=[Keyword(), Keyword(type='teardown')])
        orig = list(kws)
        assert_raises_with_msg(
            TypeError,
            "Teardown keyword type must be 'teardown', got 'setup'.",
            setattr, kws, 'teardown', Keyword(type='setup')
        )
        assert_equal(list(kws), orig)

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
