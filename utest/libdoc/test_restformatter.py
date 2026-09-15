import importlib.util
import unittest
from contextlib import redirect_stderr
from html.parser import HTMLParser
from io import StringIO

from robot.libdocpkg.htmlutils import DocFormatter, DocToHtml
from robot.libdocpkg.model import KeywordDoc


class TextCollector(HTMLParser):

    def __init__(self):
        super().__init__()
        self.text = ""

    def handle_data(self, data):
        self.text += data


@unittest.skipUnless(importlib.util.find_spec("docutils"), "Requires docutils.")
class TestRestFormatter(unittest.TestCase):

    def formatter(self, introduction=""):
        return DocFormatter([KeywordDoc(name="My Keyword")], introduction, "REST")

    def test_native_keyword_and_default_section_links(self):
        html = self.formatter().html("`My Keyword`_ and introduction_ and keywords_.")
        for target in ("My%20Keyword", "Introduction", "Keywords"):
            self.assertIn(f'href="#{target}"', html)
        self.assertNotIn("system-message", html)

    def test_introduction_section_and_explicit_external_targets(self):
        intro = (
            "Details\n=======\n\nSee site_.\n\n.. _site: https://example.com/?a=1&b=2"
        )
        formatter = self.formatter(intro)
        self.assertIn('id="details"', formatter.html(intro))
        html = formatter.html("See details_ and site_.")
        self.assertIn('href="#details"', html)
        self.assertIn('href="https://example.com/?a=1&amp;b=2"', html)

    def test_introduction_explicit_internal_target(self):
        formatter = self.formatter(".. _example:\n\nExample paragraph.")
        self.assertIn('href="#example"', formatter.html("example_"))

    def test_local_target_overrides_shared_target(self):
        html = self.formatter().html(
            "`My Keyword`_\n\n.. _My Keyword: https://example.com/"
        )
        self.assertIn('href="https://example.com/"', html)
        self.assertNotIn('href="#My%20Keyword"', html)

    def test_shared_targets_do_not_leak_between_libraries(self):
        self.formatter(".. _private: https://example.com/").html("private_")
        with redirect_stderr(StringIO()):
            html = self.formatter().html("private_")
        self.assertIn("Unknown target name", html)

    def test_unknown_reference_reports_error(self):
        with redirect_stderr(StringIO()):
            html = self.formatter().html("missing_")
        self.assertIn("Unknown target name", html)

    def test_escaped_backtick_links_are_preserved(self):
        html = self.formatter().html(r"\`My Keyword\`")
        self.assertIn('href="#My%20Keyword"', html)
        self.assertIn('class="name"', html)

    @unittest.skipUnless(importlib.util.find_spec("pygments"), "Requires Pygments.")
    def test_headerless_robot_example(self):
        html = self.formatter().html(
            "Example::\n\n    My Keyword    <value>\n    Log    ${value}"
        )
        self.assertIn('class="nf"', html)
        self.assertIn('class="nv"', html)
        self.assertNotIn("*** Keywords ***", html)
        collector = TextCollector()
        collector.feed(html)
        self.assertIn("My Keyword    <value>\nLog    ${value}", collector.text)

    def test_python_literal_is_preserved(self):
        html = self.formatter().html("Example::\n\n    def example():\n        pass")
        self.assertIn("def example():\n    pass", html)
        self.assertNotIn("robotframework", html)

    @unittest.skipUnless(importlib.util.find_spec("pygments"), "Requires Pygments.")
    def test_explicit_language_is_preserved(self):
        html = self.formatter().html(".. code:: python\n\n    print('hello')")
        self.assertIn("python", html)
        self.assertNotIn("robotframework", html)

    def test_sphinx_parameters_and_unknown_fields(self):
        html = self.formatter().html(
            "Keyword.\n\n:param str name: **User** name.\n"
            ":param count: Number of times.\n:type count: int\n"
            ":custom: Keep this field."
        )
        for text in (
            "Parameters",
            "name",
            "(str)",
            "(int)",
            "<strong>User</strong>",
            "custom",
            "Keep this field.",
        ):
            self.assertIn(text, html)
        self.assertNotIn("param str", html)
        self.assertNotIn("type count", html)

    def test_unpaired_type_field_is_preserved(self):
        html = self.formatter().html("Keyword.\n\n:type missing: int")
        self.assertIn("type missing", html)

    def test_repeated_parameter_does_not_remove_type_twice(self):
        html = self.formatter().html(
            "Keyword.\n\n:param name: First.\n:param name: Second.\n:type name: str"
        )
        self.assertIn("First.", html)
        self.assertIn("Second.", html)

    def test_explicit_text_example_is_not_highlighted(self):
        html = self.formatter().html(".. code:: text\n\n    My Keyword    argument")
        self.assertNotIn('class="nf"', html)

    def test_reference_and_literal_regressions(self):
        cases = [
            (
                "pipe",
                "Example::\n\n    | My Keyword | value |",
                "",
                '<span class="nf">My Keyword</span>',
                '<span class="nf">value</span>',
            ),
            (
                "pipe-empty",
                "Example::\n\n    | | My Keyword | value |",
                "",
                '<span class="nf">My Keyword</span>',
                '<span class="nf">value</span>',
            ),
            (
                "local-alias",
                "alias_\n\n.. _alias: `My Keyword`_",
                "",
                'href="#My%20Keyword"',
                "problematic",
            ),
            (
                "chained-alias",
                "alias_\n\n.. _alias: second_\n\n.. _second: `My Keyword`_",
                "",
                'href="#My%20Keyword"',
                "problematic",
            ),
            (
                "introduction-alias",
                "alias_",
                ".. _alias: `My Keyword`_",
                'href="#My%20Keyword"',
                "problematic",
            ),
            (
                "local-precedence",
                "alias_\n\n.. _alias: `My Keyword`_\n\n.. _My Keyword: https://example.com/local",
                "",
                'href="https://example.com/local"',
                'href="#My%20Keyword"',
            ),
            (
                "unknown-alias",
                "alias_\n\n.. _alias: missing_",
                "",
                "problematic",
                'href="#My%20Keyword"',
            ),
            (
                "ambiguous-local",
                "`My Keyword`_\n\n.. _My Keyword: https://example.com/a\n\n.. _My Keyword: https://example.com/b",
                "",
                "problematic",
                'href="#My%20Keyword"',
            ),
            (
                "literal-backticks",
                "Example::\n\n    `My Keyword`",
                "",
                "`My Keyword`",
                'href="#My%20Keyword"',
            ),
            ("inline-literal", "``My Keyword``", "", "literal", 'href="#My%20Keyword"'),
            (
                "interpreted-text",
                "`My Keyword`",
                "",
                "<cite>My Keyword</cite>",
                'href="#My%20Keyword"',
            ),
            (
                "escaped-legacy",
                r"\`My Keyword\`",
                "",
                'class="name">My Keyword</a>',
                "problematic",
            ),
            (
                "existing-link",
                r"`\`My Keyword\` <https://example.com/>`_",
                "",
                'href="https://example.com/"',
                'href="#My%20Keyword"',
            ),
        ]
        for name, doc, intro, expected, forbidden in cases:
            with self.subTest(name=name), redirect_stderr(StringIO()):
                html = self.formatter(intro).html(doc)
                self.assertIn(expected, html)
                self.assertNotIn(forbidden, html)

    def test_other_formats_are_unchanged(self):
        self.assertEqual(DocToHtml("HTML")("<b>html</b>"), "<b>html</b>")
        self.assertIn("<b>robot</b>", DocToHtml("ROBOT")("*robot*"))


if __name__ == "__main__":
    unittest.main()
