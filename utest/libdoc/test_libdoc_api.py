import json
import sys
import tempfile
import unittest
from io import StringIO

from robot import libdoc
from robot.errors import DataError
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

    def test_metadata(self):
        output = tempfile.mkstemp(suffix=".json")[1]
        libdoc.libdoc("String", output, metadata={"URL": "https://example.com"})
        with open(output, encoding="UTF-8") as f:
            data = json.load(f)
        assert_equal(data["metadata"], {"URL": "https://example.com"})

    def test_metadata_with_cli(self):
        output = tempfile.mkstemp(suffix=".json")[1]
        libdoc.libdoc_cli(
            ["--quiet", "--metadata", "URL:https://example.com", "String", output],
            exit=False,
        )
        with open(output, encoding="UTF-8") as f:
            data = json.load(f)
        assert_equal(data["metadata"], {"URL": "https://example.com"})

    def test_metadata_with_multiple_values(self):
        output = tempfile.mkstemp(suffix=".json")[1]
        libdoc.libdoc_cli(
            [
                "--quiet",
                "--metadata",
                "URL:https://example.com",
                "--metadata",
                "Source:https://github.com/example/lib",
                "--metadata",
                "URL:https://example.org",
                "String",
                output,
            ],
            exit=False,
        )
        with open(output, encoding="UTF-8") as f:
            data = json.load(f)
        assert_equal(
            data["metadata"],
            {"URL": "https://example.org", "Source": "https://github.com/example/lib"},
        )

    def test_metadata_is_omitted_when_not_used(self):
        doc = libdoc.LibraryDocumentation("String")
        assert doc.metadata == {}
        assert "metadata" not in doc.to_dictionary()

    def test_invalid_metadata(self):
        for value in ["invalid", ":value", "name:"]:
            with self.assertRaises(DataError) as context:
                libdoc.LibDoc().main(["String", "output.html"], metadata=[value])
            assert_equal(
                context.exception.message,
                f"Invalid metadata '{value}'. Metadata must be given in "
                f"'name:value' format.",
            )


if __name__ == "__main__":
    unittest.main()
