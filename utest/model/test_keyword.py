import unittest
import warnings

from robot.model import TestSuite, TestCase, Keyword, Keywords
from robot.utils import PY2, unicode
from robot.utils.asserts import (assert_equal, assert_not_equal, assert_true,
                                 assert_raises)


class TestKeyword(unittest.TestCase):

    def test_id_without_parent(self):
        assert_equal(Keyword().id, 'k1')
        assert_equal(Keyword(type=Keyword.SETUP_TYPE).id, 'k1')
        assert_equal(Keyword(type=Keyword.TEARDOWN_TYPE).id, 'k1')

    def test_suite_setup_and_teardown_id(self):
        suite = TestSuite()
        assert_equal(suite.setup.id, None)
        assert_equal(suite.teardown.id, None)
        suite.teardown.config(name='T')
        assert_equal(suite.teardown.id, 's1-k1')
        suite.setup.config(name='S')
        assert_equal(suite.setup.id, 's1-k1')
        assert_equal(suite.teardown.id, 's1-k2')

    def test_test_setup_and_teardown_id(self):
        test = TestSuite().tests.create()
        assert_equal(test.setup.id, None)
        assert_equal(test.teardown.id, None)
        test.setup.config(name='S')
        test.teardown.config(name='T')
        assert_equal(test.setup.id, 's1-t1-k1')
        assert_equal(test.teardown.id, 's1-t1-k2')
        test.body.create_keyword()
        assert_equal(test.setup.id, 's1-t1-k1')
        assert_equal(test.teardown.id, 's1-t1-k3')

    def test_test_body_id(self):
        kws = [Keyword(), Keyword(), Keyword()]
        TestSuite().tests.create().body.extend(kws)
        assert_equal([k.id for k in kws], ['s1-t1-k1', 's1-t1-k2', 's1-t1-k3'])

    def test_id_with_for_and_if_parents(self):
        t = TestCase()
        assert_equal(t.body.create_for().body.create_keyword().id, 't1-k1-k1')
        assert_equal(t.body.create_if().body.create_keyword().id, 't1-k2-k1')
        assert_equal(t.body.create_if().body.create_for().body.create_keyword().id, 't1-k3-k1-k1')

    def test_string_reprs(self):
        for kw, exp_str, exp_repr in [
            (Keyword(),
             '',
             "Keyword(name='', args=(), assign=())"),
            (Keyword('name'),
             'name',
             "Keyword(name='name', args=(), assign=())"),
            (Keyword(None),
             'None',
             "Keyword(name=None, args=(), assign=())"),
            (Keyword('Name', args=('a1', 'a2')),
             'Name    a1    a2',
             "Keyword(name='Name', args=('a1', 'a2'), assign=())"),
            (Keyword('Name', assign=('${x}', '${y}')),
             '${x}    ${y}    Name',
             "Keyword(name='Name', args=(), assign=('${x}', '${y}'))"),
            (Keyword('Name', assign=['${x}='], args=['x']),
             '${x}=    Name    x',
             "Keyword(name='Name', args=['x'], assign=['${x}='])"),
            (Keyword('Name', args=(1, 2, 3)),
             'Name    1    2    3',
             "Keyword(name='Name', args=(1, 2, 3), assign=())"),
            (Keyword(assign=[u'${\xe3}'], name=u'\xe4', args=[u'\xe5']),
             u'${\xe3}    \xe4    \xe5',
             u'Keyword(name=%r, args=[%r], assign=[%r])' % (u'\xe4', u'\xe5', u'${\xe3}'))
        ]:
            assert_equal(unicode(kw), exp_str)
            assert_equal(repr(kw), exp_repr)
            if PY2:
                assert_equal(str(kw), unicode(kw).encode('UTF-8'))

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


class TestKeywords(unittest.TestCase):

    def test_deprecation(self):
        with warnings.catch_warnings(record=True) as w:
            Keywords()
            assert_true('deprecated' in str(w[0].message))


if __name__ == '__main__':
    unittest.main()
