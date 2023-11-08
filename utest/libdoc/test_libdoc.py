import json
import os
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from robot.utils import PY_VERSION
from robot.utils.asserts import assert_equal
from robot.libdocpkg import LibraryDocumentation
from robot.libdocpkg.model import LibraryDoc, KeywordDoc
from robot.libdocpkg.htmlutils import HtmlToText

get_short_doc = HtmlToText().get_short_doc_from_html
get_text = HtmlToText().html_to_plain_text

CURDIR = Path(__file__).resolve().parent
DATADIR = (CURDIR / '../../atest/testdata/libdoc/').resolve()
TEMPDIR = Path(os.getenv('TEMPDIR') or tempfile.gettempdir())
VALIDATOR = Draft202012Validator(
    json.loads((CURDIR / '../../doc/schema/libdoc.json').read_text())
)

try:
    from typing_extensions import TypedDict
except ImportError:
    TYPEDDICT_SUPPORTS_REQUIRED_KEYS = PY_VERSION >= (3, 9)
else:
    TYPEDDICT_SUPPORTS_REQUIRED_KEYS = True


def verify_short_doc_output(doc_input, expected):
    current = get_short_doc(doc_input)
    assert_equal(current, expected)


def verify_keyword_short_doc(doc_format, doc_input, expected):
    libdoc = LibraryDoc(doc_format=doc_format)
    libdoc.keywords = [KeywordDoc(doc=doc_input)]
    assert_equal(libdoc.keywords[0].short_doc, expected)


def run_libdoc_and_validate_json(filename):
    library = DATADIR / filename
    json_spec = LibraryDocumentation(library).to_json()
    VALIDATOR.validate(instance=json.loads(json_spec))


class TestHtmlToDoc(unittest.TestCase):

    def test_short_doc_first_line(self):
        doc = """<p>This is the first line</p>
        <p>This is the second one</p>"""
        exp = "This is the first line"
        verify_short_doc_output(doc, exp)

    def test_short_doc_replace_format(self):
        doc = "<p>This is <b>bold</b> or <i>italic</i> or <i><b>italicbold</b></i> and code.</p>"
        exp = "This is *bold* or _italic_ or _*italicbold*_ and code."
        verify_short_doc_output(doc, exp)

    def test_short_doc_replace_format_multiline(self):
        doc = """<p>This is <b>bold</b>
        or <i>italic</i> or <i><b>italic
        bold</b></i> and <code>code</code>.</p>"""
        exp = """This is *bold*
        or _italic_ or _*italic
        bold*_ and ``code``."""
        verify_short_doc_output(doc, exp)

    def test_short_doc_unexcape_html(self):
        doc = """<p>This &amp; &quot;<b>&lt;b&gt;is&lt;/b&gt;</b>&quot;
        &lt;i&gt;the&lt;/i&gt; &lt;/p&gt;&apos;first&apos; line</p>"""
        exp = """This & "*<b>is</b>*"
        <i>the</i> </p>'first' line"""
        verify_short_doc_output(doc, exp)


class TestKeywordShortDoc(unittest.TestCase):

    def test_short_doc_with_multiline_plain_text(self):
        doc = """Writes the message to the console.

    If the ``newline`` argument is ``True``, a newline character is
    automatically added to the message.

    By default the message is written to the standard output stream.
    Using the standard error stream is possibly by giving the ``stream``
    argument value ``'stderr'``."""
        exp = "Writes the message to the console."
        verify_keyword_short_doc('TEXT', doc, exp)

    def test_short_doc_with_empty_plain_text(self):
        verify_keyword_short_doc('TEXT', '', '')

    def test_short_doc_with_multiline_robot_format(self):
        doc = """Writes the
*message* to
_the_ ``console``.

If the ``newline`` argument is ``True``, a newline character is
automatically added to the message.

By default the message is written to the standard output stream.
Using the standard error stream is possibly by giving the ``stream``
argument value ``'stderr'``."""
        exp = "Writes the *message* to _the_ ``console``."
        verify_keyword_short_doc('ROBOT', doc, exp)

    def test_short_doc_with_empty_robot_format(self):
        verify_keyword_short_doc('ROBOT', '', '')

    def test_short_doc_with_multiline_HTML_format(self):
        doc = """<p><strong>Writes</strong><br><em>the</em> <b>message</b>
to <i>the</i> <code>console</code>.<br><br>
If the <code>newline</code> argument is <code>True</code>, a newline character is
automatically added to the message.</p>
<p>By default the message is written to the standard output stream.
Using the standard error stream is possibly by giving the <code>stream</code>
argument value ``'stderr'``."""
        exp = "*Writes* _the_ *message* to _the_ ``console``."
        verify_keyword_short_doc('HTML', doc, exp)

    def test_short_doc_with_nonclosing_p_HTML_format(self):
        doc = """<p><strong>Writes</strong><br><em>the</em> <b>message</b>
to <i>the</i> <code>console</code>.<br><br>
If the <code>newline</code> argument is <code>True</code>, a newline character is
automatically added to the message.
<p>By default the message is written to the standard output stream.
Using the standard error stream is possibly by giving the <code>stream</code>
argument value ``'stderr'``."""
        exp = "*Writes* _the_ *message* to _the_ ``console``."
        verify_keyword_short_doc('HTML', doc, exp)

    def test_short_doc_with_empty_HTML_format(self):
        verify_keyword_short_doc('HTML', '', '')

    def test_short_doc_with_multiline_reST_format(self):
        doc = """Writes the **message**
to *the* console.

If the ``newline`` argument is ``True``, a newline character is
automatically added to the message.

By default the message is written to the standard output stream.
Using the standard error stream is possibly by giving the ``stream``
argument value ``'stderr'``."""
        exp = "Writes the **message** to *the* console."
        verify_keyword_short_doc('REST', doc, exp)

    def test_short_doc_with_empty_reST_format(self):
        verify_keyword_short_doc('REST', '', '')


class TestLibdocJsonWriter(unittest.TestCase):

    def test_Annotations(self):
        run_libdoc_and_validate_json('Annotations.py')

    def test_Decorators(self):
        run_libdoc_and_validate_json('Decorators.py')

    def test_Deprecation(self):
        run_libdoc_and_validate_json('Deprecation.py')

    def test_DocFormat(self):
        run_libdoc_and_validate_json('DocFormat.py')

    def test_DynamicLibrary(self):
        run_libdoc_and_validate_json('DynamicLibrary.py::required')

    def test_DynamicLibraryWithoutGetKwArgsAndDoc(self):
        run_libdoc_and_validate_json('DynamicLibraryWithoutGetKwArgsAndDoc.py')

    def test_ExampleSpec(self):
        run_libdoc_and_validate_json('ExampleSpec.xml')

    def test_InternalLinking(self):
        run_libdoc_and_validate_json('InternalLinking.py')

    def test_KeywordOnlyArgs(self):
        run_libdoc_and_validate_json('KeywordOnlyArgs.py')

    def test_LibraryDecorator(self):
        run_libdoc_and_validate_json('LibraryDecorator.py')

    def test_module(self):
        run_libdoc_and_validate_json('module.py')

    def test_NewStyleNoInit(self):
        run_libdoc_and_validate_json('NewStyleNoInit.py')

    def test_no_arg_init(self):
        run_libdoc_and_validate_json('no_arg_init.py')

    def test_resource(self):
        run_libdoc_and_validate_json('resource.resource')

    def test_resource_with_robot_extension(self):
        run_libdoc_and_validate_json('resource.robot')

    def test_toc(self):
        run_libdoc_and_validate_json('toc.py')

    def test_TOCWithInitsAndKeywords(self):
        run_libdoc_and_validate_json('TOCWithInitsAndKeywords.py')

    def test_TypesViaKeywordDeco(self):
        run_libdoc_and_validate_json('TypesViaKeywordDeco.py')

    def test_DynamicLibrary_json(self):
        run_libdoc_and_validate_json('DynamicLibrary.json')

    def test_DataTypesLibrary_json(self):
        run_libdoc_and_validate_json('DataTypesLibrary.json')

    def test_DataTypesLibrary_xml(self):
        run_libdoc_and_validate_json('DataTypesLibrary.xml')

    def test_DataTypesLibrary_py(self):
        run_libdoc_and_validate_json('DataTypesLibrary.py')

    def test_DataTypesLibrary_libspec(self):
        run_libdoc_and_validate_json('DataTypesLibrary.libspec')


class TestJson(unittest.TestCase):

    def test_roundtrip(self):
        self._test('DynamicLibrary.json')

    def test_roundtrip_with_datatypes(self):
        self._test('DataTypesLibrary.json')

    def _test(self, lib):
        path = DATADIR / lib
        spec = LibraryDocumentation(path).to_json()
        data = json.loads(spec)
        with open(path) as f:
            orig_data = json.load(f)
        data['generated'] = orig_data['generated'] = None
        self.maxDiff = None
        self.assertDictEqual(data, orig_data)


class TestXmlSpec(unittest.TestCase):

    def test_roundtrip(self):
        self._test('DynamicLibrary.json')

    def test_roundtrip_with_datatypes(self):
        self._test('DataTypesLibrary.json')

    def _test(self, lib):
        path = TEMPDIR / 'libdoc-utest-spec.xml'
        orig_lib = LibraryDocumentation(DATADIR / lib)
        orig_lib.save(path, format='XML')
        spec_lib = LibraryDocumentation(path)
        orig_data = orig_lib.to_dictionary()
        spec_data = spec_lib.to_dictionary()
        orig_data['generated'] = spec_data['generated'] = None
        self.maxDiff = None
        self.assertDictEqual(orig_data, spec_data)


class TestLibdocTypedDictKeys(unittest.TestCase):

    def test_typed_dict_keys(self):
        library = DATADIR / 'DataTypesLibrary.py'
        spec = LibraryDocumentation(library).to_json()
        current_items = json.loads(spec)['typedocs'][7]['items']
        expected_items = [
            {
                "key": "longitude",
                "type": "float",
                "required": True if TYPEDDICT_SUPPORTS_REQUIRED_KEYS else None
            },
            {
                "key": "latitude",
                "type": "float",
                "required": True if TYPEDDICT_SUPPORTS_REQUIRED_KEYS else None
            },
            {
                "key": "accuracy",
                "type": "float",
                "required": False if TYPEDDICT_SUPPORTS_REQUIRED_KEYS else None
            }
        ]
        for exp_item in expected_items:
            for cur_item in current_items:
                if exp_item['key'] == cur_item['key']:
                    assert_equal(exp_item, cur_item)
                    break


if __name__ == '__main__':
    unittest.main()
