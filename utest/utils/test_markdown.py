import sys
import unittest

from robot.errors import DataError
from robot.utils.asserts import assert_raises_with_msg
from robot.utils.markdown import AdmonitionExtension, LinkifyExtension, Markdown


def assert_markdown(text, expected=None):
    extensions = [AdmonitionExtension(), LinkifyExtension()]
    actual = Markdown(extensions=extensions).convert(text)
    if not expected:
        expected = Markdown().convert(text)
    elif not expected.strip().startswith(("<div", "<blockquote")):
        expected = f"<p>{expected}</p>"
    else:
        expected = expected.strip()
    if actual != expected:
        raise AssertionError(
            f"Markdown conversion failed.\n\n"
            f"Input:\n{text!r}\n\n"
            f"Expected:\n{expected!r}\n\n"
            f"Actual:\n{actual!r}\n"
        )


class TestLinkifyUrls(unittest.TestCase):

    def test_no_urls(self):
        for text in ["", "Hello!", "*Hi!*", "two\nlines"]:
            assert_markdown(text)

    def test_url_that_should_not_be_touched(self):
        for text in [
            "[example](http://example.com)",
            '[example](http://example.com "Title with http://example.com")',
            "<http://example.com>",
            "`http://example.com`",
        ]:
            assert_markdown(text)
            assert_markdown(f"This is {text}!")

    def test_linkify_urls(self):
        for text, expected in [
            ("ftp://example.com", '<a href="ftp://example.com">ftp://example.com</a>'),
            ("git+ssh://h/p/", '<a href="git+ssh://h/p/">git+ssh://h/p/</a>'),
            ("A-B.c://d/e?f#g", '<a href="A-B.c://d/e?f#g">A-B.c://d/e?f#g</a>'),
            ("file:///c:/p/f.e", '<a href="file:///c:/p/f.e">file:///c:/p/f.e</a>'),
            ("a://1, b://2", '<a href="a://1">a://1</a>, <a href="b://2">b://2</a>'),
        ]:
            assert_markdown(text, expected)
            assert_markdown(f"This is {text}!", f"This is {expected}!")
            for end in [",", ".", ";", ":", "!", "?", "...", "!?!", " hello", "\n2"]:
                assert_markdown(text + end, expected + end)
                assert_markdown("start " + text + end, "start " + expected + end)
            for start, end in [("(", ")"), ("[", "]"), ('"', '"'), ("'", "'")]:
                assert_markdown(start + text + end, start + expected + end)


class TestAdmonitions(unittest.TestCase):

    def test_basics(self):
        markdown = """
> [!NOTE]
> Body that can span multiple
> lines and contain *formatting*.
"""
        expected = """
<div class="admonition note">
<p class="admonition-title">Note</p>
<p>Body that can span multiple
lines and contain <em>formatting</em>.</p>
</div>
"""
        assert_markdown(markdown, expected)

    def test_kind_can_be_anything(self):
        markdown = """
> [!{}]
> Body.
"""
        expected = """
<div class="admonition {}">
<p class="admonition-title">{}</p>
<p>Body.</p>
</div>
"""
        for kind in ["note", "tip", "important", "warning", "caution", "danger", "xxx"]:
            exp = expected.format(kind.lower(), kind.capitalize())
            assert_markdown(markdown.format(kind.lower()), exp)
            assert_markdown(markdown.format(kind.upper()), exp)
            assert_markdown(markdown.format(kind.title()), exp)

    def test_optional_title(self):
        markdown = """
> [!tip] {}
> Body.
"""
        expected = """
<div class="admonition tip">
<p class="admonition-title">{}</p>
<p>Body.</p>
</div>
"""
        for title in ["Title!", "Two words", "[!title]"]:
            assert_markdown(markdown.format(title), expected.format(title))

    def test_whitespace(self):
        markdown = """
>   [!note]  Title  here!
>
> First paragraph.
>
> Second paragraph.
>

> Outside note.
"""
        expected = """
<div class="admonition note">
<p class="admonition-title">Title  here!</p>
<p>First paragraph.</p>
<p>Second paragraph.
</p>
</div>
<blockquote>
<p>Outside note.</p>
</blockquote>
"""
        assert_markdown(markdown, expected)

    def test_broken_header(self):
        markdown = """
> [!broken
> Body.
"""
        expected = """
<blockquote>
<p>[!broken
Body.</p>
</blockquote>
"""
        assert_markdown(markdown, expected)

    def test_empty_body(self):
        expected = """
<div class="admonition note">
<p class="admonition-title">Note</p>
</div>
"""
        for markdown in ("> [!note]", "> [!note]\n>"):
            assert_markdown(markdown, expected)

    def test_nested(self):
        markdown = """
> [!caution]
> > [!note]
> > Nesting is not supported by all tools!
>
> Back in caution.
"""
        expected = """
<div class="admonition caution">
<p class="admonition-title">Caution</p>
<div class="admonition note">
<p class="admonition-title">Note</p>
<p>Nesting is not supported by all tools!</p>
</div>
<p>Back in caution.</p>
</div>
"""
        assert_markdown(markdown, expected)


class TestMarkdownNotInstalled(unittest.TestCase):

    def setUp(self):
        # Invalidate cache entry to ensure importing 'markdown' fails.
        sys.modules["markdown"] = None
        sys.modules.pop("robot.utils.markdown")

    def test_markdown_not_installed(self):
        from robot.utils.markdown import Markdown

        assert_raises_with_msg(
            DataError,
            "Markdown format requires 'markdown' module to be installed.",
            Markdown,
        )

    def tearDown(self):
        # Cleanup invalid modules. If they are needed later, they are reimported.
        sys.modules.pop("markdown")
        sys.modules.pop("robot.utils.markdown")


if __name__ == "__main__":
    unittest.main()
