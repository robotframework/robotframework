import unittest

from robot.model.metadata import Metadata
from robot.utils import PY2, PY3
from robot.utils.asserts import assert_equal


if PY3:
    unicode = str


class TestMetadata(unittest.TestCase):

    def test_normalizetion(self):
        md = Metadata([('m1', 1), ('M2', 1), ('m_3', 1), ('M1', 2), ('M 3', 2)])
        assert_equal(dict(md), {'m1': 2, 'M2': 1, 'm_3': 2})

    def test_unicode(self):
        assert_equal(unicode(Metadata()), u'{}')
        d = {'a': 1, 'B': 'two', u'\xe4': u'nelj\xe4'}
        assert_equal(unicode(Metadata(d)), u'{a: 1, B: two, \xe4: nelj\xe4}')

    if PY2:
        def test_str(self):
            assert_equal(str(Metadata()), '{}')
            d = {'a': 1, 'B': 'two', u'\xe4': u'nelj\xe4'}
            assert_equal(str(Metadata(d)),
                         u'{a: 1, B: two, \xe4: nelj\xe4}'.encode('UTF-8'))


if __name__ == '__main__':
    unittest.main()
