import unittest
import os

from robot import utils
from robot.utils.asserts import assert_equals


class TestEncoding(unittest.TestCase):

    def test_file_system_encoding(self):
        assert_equals(utils.encoding.file_system_encoding, 'UTF-8')

    def test_encoding_to_file_system(self):
        assert_equals(utils.encoding.encode_to_file_system(u'\xe4'), '\xc3\xa4')

    def test_output_encoding(self):
        assert_equals(utils.encoding.output_encoding, 'UTF-8')

    def test_decoding_output(self):
        assert_equals(utils.encoding.decode_output('\xc3\xa4'), u'\xe4')

    def test_reading_from_lang_environment_var(self):
        assert_equals(utils.encoding._read_encoding_from_env(), 'UTF-8')

    def test_reading_from_lc_ctype_environment_var(self):
        os.environ = {'LC_CTYPE': 'ascii'}
        assert_equals(utils.encoding._read_encoding_from_env(), 'ascii')


if __name__ == '__main__':
    unittest.main()
