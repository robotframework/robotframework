import unittest

from robot.utils.asserts import assert_equal
from robot.utils.encoding import console_decode, console_encode, CONSOLE_ENCODING


UNICODE = 'hyvä'
ENCODED = UNICODE.encode(CONSOLE_ENCODING)


class TestConsoleDecode(unittest.TestCase):

    def test_decode(self):
        assert_equal(console_decode(ENCODED), UNICODE)

    def test_unicode_is_returned_as_is(self):
        assert_equal(console_decode(UNICODE), UNICODE)


class TestConsoleEncode(unittest.TestCase):

    def test_unicode_is_returned_as_is_by_default(self):
        assert_equal(console_encode(UNICODE), UNICODE)

    def test_force_encoding(self):
        assert_equal(console_encode(UNICODE, 'UTF-8', force=True), b'hyv\xc3\xa4')

    def test_encoding_error(self):
        assert_equal(console_encode(UNICODE, 'ASCII'), 'hyv?')
        assert_equal(console_encode(UNICODE, 'ASCII', force=True), b'hyv?')

    def test_non_string(self):
        assert_equal(console_encode(42), '42')


if __name__ == '__main__':
    unittest.main()
