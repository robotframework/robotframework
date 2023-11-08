import unittest

from robot.libdocpkg.standardtypes import STANDARD_TYPE_DOCS
from robot.running.arguments.typeconverters import (
    EnumConverter, CustomConverter, TypeConverter, TypedDictConverter, UnionConverter
)


class TestStandardTypeDocs(unittest.TestCase):
    no_std_docs = (EnumConverter, CustomConverter, TypedDictConverter, UnionConverter)

    def test_all_standard_types_have_docs(self):
        for cls in TypeConverter.__subclasses__():
            if cls.type not in STANDARD_TYPE_DOCS and cls not in self.no_std_docs:
                raise AssertionError(f"Standard converter '{cls.__name__}' "
                                     f"does not have documentation.")


if __name__ == '__main__':
    unittest.main()
