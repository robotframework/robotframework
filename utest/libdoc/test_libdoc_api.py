import sys
import tempfile
import unittest
from io import StringIO

from robot import libdoc
from robot.utils.asserts import assert_equal


class TestLibdoc(unittest.TestCase):

    def setUp(self):
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_html(self):
        output = tempfile.mkstemp(suffix=".html")[1]
        libdoc.libdoc("String", output)
        assert_equal(sys.stdout.getvalue().strip(), output)
        with open(output, encoding="UTF-8") as f:
            assert '"name": "String"' in f.read()

    def test_xml(self):
        output = tempfile.mkstemp(suffix=".xml")[1]
        libdoc.libdoc("String", output)
        assert_equal(sys.stdout.getvalue().strip(), output)
        with open(output, encoding="UTF-8") as f:
            assert 'name="String"' in f.read()

    def test_format(self):
        output = tempfile.mkstemp()[1]
        libdoc.libdoc("String", output, format="xml")
        assert_equal(sys.stdout.getvalue().strip(), output)
        with open(output, encoding="UTF-8") as f:
            assert 'name="String"' in f.read()

    def test_quiet(self):
        output = tempfile.mkstemp(suffix=".html")[1]
        libdoc.libdoc("String", output, quiet=True)
        assert_equal(sys.stdout.getvalue().strip(), "")
        with open(output, encoding="UTF-8") as f:
            assert '"name": "String"' in f.read()

    def test_LibraryDocumentation(self):
        doc = libdoc.LibraryDocumentation("OperatingSystem")
        assert_equal(doc.name, "OperatingSystem")

    def test_operating_system_docs_use_markdown_and_document_arguments(self):
        doc = libdoc.LibraryDocumentation("OperatingSystem")
        assert_equal(doc.doc_format, "MARKDOWN")
        for keyword in doc.keywords:
            for argument in keyword.args:
                self.assertTrue(
                    argument.doc,
                    f"{keyword.name}: argument '{argument.name}' has no documentation",
                )
            data = keyword.to_dictionary()
            if data["returnType"]:
                self.assertTrue(
                    data["returnDoc"],
                    f"{keyword.name}: return value has no documentation",
                )


if __name__ == "__main__":
    unittest.main()
