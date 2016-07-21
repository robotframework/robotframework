import unittest
import zlib

from robot.utils.compress import compress_text, _compress
from robot.utils.asserts import assert_equal, assert_true


class TestCompress(unittest.TestCase):

    def _test(self, text):
        assert_true(isinstance(compress_text(text), str))
        text = text.encode('UTF-8')
        assert_equal(_compress(text), zlib.compress(text, 9))

    def test_empty_string(self):
        self._test('')

    def test_100_char_strings(self):
        self._test('100 Somewhat Random Chars ... als 13 asd 20a \n'
                   'Rsakjaf AdfSasda  asldjfaerew lasldjf awlkr aslk sd rl')

    def test_non_ascii(self):
        self._test(u'hyv\xe4')
        self._test(u'\u4e2d\u6587')


if __name__ == '__main__':
    unittest.main()
