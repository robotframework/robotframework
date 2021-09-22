import codecs
import os
import tempfile
import unittest
from io import BytesIO, StringIO
from pathlib import Path

from robot.utils import FileReader
from robot.utils.asserts import assert_equal, assert_raises


TEMPDIR = os.getenv('TEMPDIR') or tempfile.gettempdir()
PATH = os.path.join(TEMPDIR, 'filereader.test')
STRING = u'Hyv\xe4\xe4\nty\xf6t\xe4\nC\u043f\u0430\u0441\u0438\u0431\u043e\n'


def assert_reader(reader, name=PATH):
    assert_equal(reader.read(), STRING, formatter=repr)
    assert_equal(reader.name, name)
    assert_open(reader.file)


def assert_open(*files):
    for f in files:
        assert_equal(f.closed, False)


def assert_closed(*files):
    for f in files:
        assert_equal(f.closed, True)


class TestReadFile(unittest.TestCase):
    BOM = b''
    created_files = set()

    @classmethod
    def setUpClass(cls):
        cls._create()

    @classmethod
    def _create(cls, content=STRING, path=PATH, encoding='UTF-8'):
        with open(path, 'wb') as f:
            f.write(cls.BOM)
            f.write(content.replace('\n', os.linesep).encode(encoding))
        cls.created_files.add(path)

    @classmethod
    def tearDownClass(cls):
        for path in cls.created_files:
            os.remove(path)
        cls.created_files = set()

    def test_path_as_string(self):
        with FileReader(PATH) as reader:
            assert_reader(reader)
        assert_closed(reader.file)

    def test_open_text_file(self):
        with open(PATH, encoding='UTF-8') as f:
            with FileReader(f) as reader:
                assert_reader(reader)
            assert_open(f, reader.file)
        assert_closed(f, reader.file)

    def test_path_as_pathlib_path(self):
        with FileReader(Path(PATH)) as reader:
            assert_reader(reader)
        assert_closed(reader.file)

    def test_codecs_open_file(self):
        with codecs.open(PATH, encoding='UTF-8') as f:
            with FileReader(f) as reader:
                assert_reader(reader)
            assert_open(f, reader.file)
        assert_closed(f, reader.file)

    def test_open_binary_file(self):
        with open(PATH, 'rb') as f:
            with FileReader(f) as reader:
                assert_reader(reader)
            assert_open(f, reader.file)
        assert_closed(f, reader.file)

    def test_stringio(self):
        f = StringIO(STRING)
        with FileReader(f) as reader:
            assert_reader(reader, '<in-memory file>')
        assert_open(f)

    def test_bytesio(self):
        f = BytesIO(self.BOM + STRING.encode('UTF-8'))
        with FileReader(f) as reader:
            assert_reader(reader, '<in-memory file>')
        assert_open(f)

    def test_accept_text(self):
        with FileReader(STRING, accept_text=True) as reader:
            assert_reader(reader, '<in-memory file>')
        assert_closed(reader.file)

    def test_no_accept_text(self):
        assert_raises(IOError, FileReader, STRING)

    def test_readlines(self):
        with FileReader(PATH) as reader:
            assert_equal(list(reader.readlines()), STRING.splitlines(True))

    def test_invalid_encoding(self):
        russian = STRING.split()[-1]
        path = os.path.join(TEMPDIR, 'filereader.iso88595')
        self._create(russian, path, encoding='ISO-8859-5')
        with FileReader(path) as reader:
            assert_raises(UnicodeDecodeError, reader.read)


class TestReadFileWithBom(TestReadFile):
    BOM = codecs.BOM_UTF8


if __name__ == '__main__':
    unittest.main()
