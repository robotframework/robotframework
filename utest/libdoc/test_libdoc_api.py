from io import StringIO
import sys
import tempfile
import unittest

from robot import libdoc
from robot.utils.asserts import assert_equal


class TestLibdoc(unittest.TestCase):

    def setUp(self):
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_html(self):
        output = tempfile.mkstemp(suffix='.html')[1]
        libdoc.libdoc('String', output)
        assert_equal(sys.stdout.getvalue().strip(), output)
        with open(output) as f:
            assert '"name": "String"' in f.read()

    def test_xml(self):
        output = tempfile.mkstemp(suffix='.xml')[1]
        libdoc.libdoc('String', output)
        assert_equal(sys.stdout.getvalue().strip(), output)
        with open(output) as f:
            assert 'name="String"' in f.read()

    def test_format(self):
        output = tempfile.mkstemp()[1]
        libdoc.libdoc('String', output, format='xml')
        assert_equal(sys.stdout.getvalue().strip(), output)
        with open(output) as f:
            assert 'name="String"' in f.read()

    def test_quiet(self):
        output = tempfile.mkstemp(suffix='.html')[1]
        libdoc.libdoc('String', output, quiet=True)
        assert_equal(sys.stdout.getvalue().strip(), '')
        with open(output) as f:
            assert '"name": "String"' in f.read()

    def test_LibraryDocumentation(self):
        doc = libdoc.LibraryDocumentation('OperatingSystem')
        assert_equal(doc.name, 'OperatingSystem')


if __name__ == '__main__':
    unittest.main()
