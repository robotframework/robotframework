import unittest
import sys

from robot.utils.asserts import assert_equals
from robot.utils.encoding import decode_output, OUTPUT_ENCODING


UNICODE = u'hyv\xe4'
ENCODED = UNICODE.encode(OUTPUT_ENCODING)
IRONPYTHON = sys.platform == 'cli'


class TestDecodeOutput(unittest.TestCase):

    def test_return_unicode_as_is_by_default(self):
        assert isinstance(UNICODE, unicode)
        assert_equals(decode_output(UNICODE), UNICODE)

    if not IRONPYTHON:

        def test_decode(self):
            assert isinstance(ENCODED, str)
            assert_equals(decode_output(ENCODED), UNICODE)

    else:

        def test_force_decoding(self):
            assert isinstance(ENCODED, unicode)
            assert_equals(decode_output(ENCODED, force=True), UNICODE)


if __name__ == '__main__':
    unittest.main()
