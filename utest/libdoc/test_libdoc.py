import unittest

from robot.utils.asserts import assert_equal
from robot.libdocpkg.model import LibraryDoc, KeywordDoc
from robot.libdocpkg.htmlwriter import HtmlToText, DocToHtml

get_shortdoc = HtmlToText().get_shortdoc_from_html
get_text = HtmlToText().html_to_plain_text


def verify_shortdoc_output(doc_input, expected):
    current = get_shortdoc(doc_input)
    assert_equal(current, expected)


def verify_keyword_shortdoc(doc_format, doc_input, expected):
    libdoc = LibraryDoc(doc_format=doc_format)
    libdoc.keywords = [KeywordDoc(doc=doc_input)]
    formatter = DocToHtml(doc_format)
    keyword = libdoc.keywords[0]
    keyword.doc = formatter(keyword.doc)
    libdoc.doc_format = 'HTML'
    assert_equal(keyword.shortdoc, expected)


class TestHtmlToDoc(unittest.TestCase):

    def test_shortdoc_firstline(self):
        doc = """<p>This is the first line</p>
        <p>This is the second one</p>"""
        exp = "This is the first line"
        verify_shortdoc_output(doc, exp)

    def test_shortdoc_replace_format(self):
        doc = "<p>This is <b>bold</b> or <i>italic</i> or <i><b>italicbold</b></i> and code.</p>"
        exp = "This is *bold* or _italic_ or _*italicbold*_ and code."
        verify_shortdoc_output(doc, exp)

    def test_shortdoc_replace_format_multiline(self):
        doc = """<p>This is <b>bold</b>
        or <i>italic</i> or <i><b>italic
        bold</b></i> and <code>code</code>.</p>"""
        exp = """This is *bold*
        or _italic_ or _*italic
        bold*_ and ``code``."""
        verify_shortdoc_output(doc, exp)

    def test_shortdoc_unexcape_html(self):
        doc = """<p>This &amp; &quot;<b>&lt;b&gt;is&lt;/b&gt;</b>&quot;
        &lt;i&gt;the&lt;/i&gt; &lt;/p&gt;&apos;first&apos; line</p>"""
        exp = """This & "*<b>is</b>*"
        <i>the</i> </p>'first' line"""
        verify_shortdoc_output(doc, exp)


class TestKeywordDoc(unittest.TestCase):

    def test_shortdoc_with_multiline_plain_text(self):
        doc = """Writes the message to the console.

If the ``newline`` argument is ``True``, a newline character is
automatically added to the message.

By default the message is written to the standard output stream.
Using the standard error stream is possibly by giving the ``stream``
argument value ``'stderr'``."""
        exp = "Writes the message to the console."
        verify_keyword_shortdoc('TEXT', doc, exp)

    def test_shortdoc_with_multiline_robot_format(self):
        doc = """Writes the
*message* to
_the_ ``console``.

If the ``newline`` argument is ``True``, a newline character is
automatically added to the message.

By default the message is written to the standard output stream.
Using the standard error stream is possibly by giving the ``stream``
argument value ``'stderr'``."""
        exp = "Writes the *message* to _the_ ``console``."
        verify_keyword_shortdoc('ROBOT', doc, exp)

    def test_shortdoc_with_multiline_HTML_format(self):
        doc = """<p><strong>Writes</strong><br><em>the</em> <b>message</b>
to <i>the</i> <code>console</code>.<br><br>
If the <code>newline</code> argument is <code>True</code>, a newline character is
automatically added to the message.</p>
<p>By default the message is written to the standard output stream.
Using the standard error stream is possibly by giving the <code>stream</code>
argument value ``'stderr'``."""
        exp = "*Writes* _the_ *message* to _the_ ``console``."
        verify_keyword_shortdoc('HTML', doc, exp)
