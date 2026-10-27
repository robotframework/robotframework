import unittest
from datetime import timedelta

from robot.api.types import Secret
from robot.libdocpkg import standardtypes
from robot.libdocpkg.htmlutils import DocToHtml
from robot.running.arguments.typeconverters import (
    CustomConverter, EnumConverter, RecursiveConverter, TypeConverter,
    TypedDictConverter, UnionConverter, UnknownConverter
)


class TestStandardTypeDocs(unittest.TestCase):
    no_std_docs = (
        CustomConverter,
        EnumConverter,
        RecursiveConverter,
        TypedDictConverter,
        UnionConverter,
        UnknownConverter,
    )

    def test_all_standard_types_have_docs(self):
        for cls in TypeConverter.__subclasses__():
            self._assert_doc_exists(cls, standardtypes._std_docs_robot, "Robot")
            self._assert_doc_exists(cls, standardtypes._std_docs_markdown, "Markdown")

    def _assert_doc_exists(self, cls, docs, fmt):
        if cls.type not in docs and cls not in self.no_std_docs:
            raise AssertionError(f"{cls.__name__} does not have docs in {fmt} format.")

    def test_links_in_rest_docs_work(self):
        self._assert_rest_link(
            timedelta,
            "Robot Framework User Guide",
            "https://robotframework.org/robotframework/",
        )
        self._assert_rest_link(
            Secret,
            "robot.api.types.Secret",
            "https://robot-framework.readthedocs.io/en/master/autodoc/robot.utils.html#robot.utils.secret.Secret",
        )

    def _assert_rest_link(self, typ, title, href):
        html = DocToHtml("REST")(standardtypes.get_standard_type_doc(typ, "reST"))
        link = f'<a class="reference external" href="{href}">{title}</a>'
        self.assertIn(link, html)

    def test_no_rest_errors(self):
        for typ in standardtypes._std_docs_robot:
            html = DocToHtml("REST")(standardtypes.get_standard_type_doc(typ, "reST"))
            self.assertNotIn("ERROR", html)
            self.assertNotIn("WARNING", html)


if __name__ == "__main__":
    unittest.main()
