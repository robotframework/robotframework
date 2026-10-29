"""Tests for robot.libdocpkg.htmlutils docutils integration.

Covers the docutils 0.22 change that merged ``writer_name`` into ``writer``
(issue #5838): the deprecation warning must not fire when reST documentation
is formatted, and the chosen keyword argument must match the installed
docutils signature (Robot Framework pins no docutils version).
"""

import unittest
import warnings
from inspect import signature

try:
    import docutils
    from docutils.core import publish_parts
except ImportError:
    docutils = None

from robot.libdocpkg.htmlutils import DocToHtml, _WRITER_KWARG


@unittest.skipIf(docutils is None, "docutils not installed")
class TestRestWriterKeyword(unittest.TestCase):

    def test_formatting_rest_emits_no_writer_name_deprecation(self):
        formatter = DocToHtml("rest")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            html = formatter("Some *rest* doc with ``code`` and *emphasis*.")
        self.assertIn("emphasis", html)
        deprecations = [w for w in caught if "writer_name" in str(w.message)]
        self.assertEqual(deprecations, [])

    def test_chosen_keyword_matches_installed_docutils_signature(self):
        has_writer = "writer" in signature(publish_parts).parameters
        if has_writer:
            self.assertEqual(_WRITER_KWARG, {"writer": "html"})
        else:
            self.assertEqual(_WRITER_KWARG, {"writer_name": "html"})

    def test_rest_output_content_unchanged(self):
        html = DocToHtml("rest")("Title\n=====\n\nBody text.")
        self.assertIn("Body text.", html)
        self.assertIn("Title", html)


if __name__ == "__main__":
    unittest.main()
