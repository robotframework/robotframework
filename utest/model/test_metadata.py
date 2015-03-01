from six import text_type as unicode

import sys
import unittest

from robot.utils.asserts import assert_equal
from robot.model.metadata import Metadata


class TestMetadata(unittest.TestCase):

    def test_normalizetion(self):
        md = Metadata([('m1', 1), ('M2', 1), ('m_3', 1), ('M1', 2), ('M 3', 2)])
        assert_equal(dict(md), {'m1': 2, 'M2': 1, 'm_3': 2})

    def test_unicode(self):
        assert_equal(unicode(Metadata()), u'{}')
        d = {'a': 1, 'B': 'two', u'\xe4': u'nelj\xe4'}
        assert_equal(unicode(Metadata(d)), u'{a: 1, B: two, \xe4: nelj\xe4}')

    if sys.version_info[0] < 3:
        def test_str(self):
            assert_equal(str(Metadata()), '{}')
            d = {'a': 1, 'B': 'two', u'\xe4': u'nelj\xe4'}
            assert_equal(str(Metadata(d)), '{a: 1, B: two, ?: nelj?}')

    else:
        def test_bytes(self):
            assert_equal(bytes(Metadata()), '{}'.encode())
            d = {'a': 1, 'B': 'two', u'\xe4': u'nelj\xe4'}
            assert_equal(bytes(Metadata(d)), '{a: 1, B: two, ?: nelj?}'.encode())


if __name__ == '__main__':
    unittest.main()
