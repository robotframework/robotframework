import unittest

from robot.utils import IRONPYTHON, PY3
from robot.utils.asserts import assert_equals
from robot.utils.encoding import decode_output, OUTPUT_ENCODING


UNICODE = u'hyv\xe4'
ENCODED = UNICODE.encode(OUTPUT_ENCODING)


class TestDecodeOutput(unittest.TestCase):

    def test_return_unicode_as_is_by_default(self):
        assert_equals(decode_output(UNICODE), UNICODE)

    if not IRONPYTHON:

        def test_decode(self):
            assert_equals(decode_output(ENCODED), UNICODE)

    else:

        assert isinstance(ENCODED, unicode)

        def test_force_decoding(self):
            assert_equals(decode_output(ENCODED, force=True), UNICODE)

        def test_bytes_are_decoded(self):
            assert_equals(decode_output(bytes(ENCODED)), UNICODE)


if __name__ == '__main__':
    unittest.main()
