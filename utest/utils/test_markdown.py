import unittest

from robot.utils.markdown import LinkifyExtension, Markdown


def assert_markdown(text, expected=None, **config):
    extensions = config.pop("extensions", []) + [LinkifyExtension()]
    actual = Markdown(extensions=extensions, **config).convert(text)
    expected = Markdown().convert(text) if expected is None else f"<p>{expected}</p>"
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


if __name__ == "__main__":
    unittest.main()
