import unittest

from robot.utils import IRONPYTHON, PY3
from robot.utils.asserts import assert_equal
from robot.utils.encoding import console_decode, CONSOLE_ENCODING


UNICODE = u'hyv\xe4'
ENCODED = UNICODE.encode(CONSOLE_ENCODING)


class TestDecodeOutput(unittest.TestCase):

    def test_return_unicode_as_is_by_default(self):
        assert_equal(console_decode(UNICODE), UNICODE)

    if not IRONPYTHON:

        def test_decode(self):
            assert_equal(console_decode(ENCODED), UNICODE)

    else:

        assert isinstance(ENCODED, unicode)

        def test_force_decoding(self):
            assert_equal(console_decode(ENCODED, force=True), UNICODE)

        def test_bytes_are_decoded(self):
            assert_equal(console_decode(bytes(ENCODED)), UNICODE)


if __name__ == '__main__':
    unittest.main()
