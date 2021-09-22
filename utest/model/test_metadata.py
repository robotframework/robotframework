import unittest

from robot.model.metadata import Metadata
from robot.utils.asserts import assert_equal


class TestMetadata(unittest.TestCase):

    def test_normalization(self):
        md = Metadata([('m1', 'xxx'), ('M2', 'xxx'), ('m_3', 'xxx'),
                       ('M1', 'YYY'), ('M 3', 'YYY')])
        assert_equal(dict(md), {'m1': 'YYY', 'M2': 'xxx', 'm_3': 'YYY'})

    def test_str(self):
        assert_equal(str(Metadata()), '{}')
        d = {'a': 1, 'B': 'two', 'ä': 'neljä'}
        assert_equal(str(Metadata(d)), '{a: 1, B: two, ä: neljä}')

    def test_non_string_items(self):
        md = Metadata([('number', 42), ('boolean', True), (1, 'one')])
        assert_equal(md['number'], '42')
        assert_equal(md['boolean'], 'True')
        assert_equal(md['1'], 'one')
        md['number'] = 1.0
        md['boolean'] = False
        md['new'] = []
        md[True] = ''
        assert_equal(md['number'], '1.0')
        assert_equal(md['boolean'], 'False')
        assert_equal(md['new'], '[]')
        assert_equal(md['True'], '')
        md.setdefault('number', 99)
        md.setdefault('setdefault', 99)
        assert_equal(md['number'], '1.0')
        assert_equal(md['setdefault'], '99')


if __name__ == '__main__':
    unittest.main()
