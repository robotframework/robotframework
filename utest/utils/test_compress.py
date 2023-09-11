import base64
import unittest
import zlib

from robot.utils.compress import compress_text
from robot.utils.asserts import assert_equal, assert_true


class TestCompress(unittest.TestCase):

    def _test(self, text):
        compressed = compress_text(text)
        assert_true(isinstance(compressed, str))
        uncompressed = zlib.decompress(base64.b64decode(compressed)).decode('UTF-8')
        assert_equal(uncompressed, text)

    def test_empty_string(self):
        self._test('')

    def test_100_char_strings(self):
        self._test('100 Somewhat Random Chars ... als 13 asd 20a \n'
                   'Rsakjaf AdfSasda  asldjfaerew lasldjf awlkr aslk sd rl')

    def test_non_ascii(self):
        self._test('hyvä')
        self._test('中文')


if __name__ == '__main__':
    unittest.main()
