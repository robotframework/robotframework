import unittest

from robot.libdocpkg import standardtypes
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
            self._assert(cls, standardtypes._std_docs_robot, "Robot")
            self._assert(cls, standardtypes._std_docs_markdown, "Markdown")

    def _assert(self, cls, docs, fmt):
        if cls.type not in docs and cls not in self.no_std_docs:
            raise AssertionError(f"{cls.__name__} does not have docs in {fmt} format.")


if __name__ == "__main__":
    unittest.main()
