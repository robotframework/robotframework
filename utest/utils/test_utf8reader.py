import os
import tempfile
import unittest
from codecs import BOM_UTF8
from io import BytesIO

from robot.utils import Utf8Reader
from robot.utils.asserts import assert_equals, assert_raises


PATH = os.path.join(tempfile.gettempdir(), 'test_utf8reader.xml')
STRING = u'Hyv\xe4\xe4\nty\xf6t\xe4\n.C\u043f\u0430\u0441\u0438\u0431\u043e'


class TestUtf8ReaderWithBom(unittest.TestCase):
    BOM = BOM_UTF8

    def setUp(self):
        self._create()

    def _create(self, content=STRING, encoding='UTF-8'):
        with open(PATH, 'wb') as f:
            inn = self.BOM + content.encode(encoding)
            f.write(inn)

    def tearDown(self):
        os.remove(PATH)

    def test_read(self):
        with Utf8Reader(PATH) as reader:
            f = reader._file
            assert_equals(reader.read(), STRING)
        assert_equals(f.closed, True)

    def test_read_open_file(self):
        with open(PATH, 'rb') as f:
            with Utf8Reader(f) as reader:
                assert_equals(reader.read(), STRING)
            assert_equals(f.closed, False)

    def test_must_open_in_binary_mode(self):
        with open(PATH, 'r') as f:
            assert_raises(ValueError, Utf8Reader, f)

    def test_stringio_is_ok(self):
        f = BytesIO(self.BOM + STRING.encode('UTF-8'))
        with Utf8Reader(f) as reader:
            assert_equals(reader.read(), STRING)
        assert_equals(f.closed, False)

    def test_readlines(self):
        with Utf8Reader(PATH) as reader:
            assert_equals(list(reader.readlines()), STRING.splitlines(True))

    def test_invalid_encoding(self):
        self._create(STRING.splitlines()[-1], 'ISO-8859-5')
        with Utf8Reader(PATH) as reader:
            assert_raises(UnicodeDecodeError, reader.read)


class TestUtf8ReaderWithoutBom(TestUtf8ReaderWithBom):
    BOM = b''


if __name__ == '__main__':
    unittest.main()
