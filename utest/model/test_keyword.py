import unittest
import warnings
from robot.utils.asserts import (assert_equal, assert_none, assert_not_equal,
                                 assert_true, assert_raises, assert_raises_with_msg)

from robot.model import TestSuite, Message
from robot.model.keyword import Keyword, Keywords
from robot.utils import PY2, unicode


class TestKeyword(unittest.TestCase):

    def test_id_without_parent(self):
        assert_equal(Keyword().id, 'k1')

    def test_id_with_suite_parent(self):
        assert_equal(TestSuite().setup.config(name='KW').id, 's1-k1')

    def test_id_with_test_parent(self):
        assert_equal(TestSuite().tests.create().body.create().id, 's1-t1-k1')

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

    def test_deprecation(self):
        with warnings.catch_warnings(record=True) as w:
            Keywords()
            assert_true('deprecated' in str(w[0].message))


if __name__ == '__main__':
    unittest.main()
