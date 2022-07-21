import unittest

from robot.api import Language
from robot.conf.languages import Fi, PtBr
from robot.utils.asserts import assert_raises_with_msg


class TestFromName(unittest.TestCase):

    def test_class_name(self):
        assert isinstance(Language.from_name('fi'), Fi)
        assert isinstance(Language.from_name('FI'), Fi)

    def test_docstring(self):
        assert isinstance(Language.from_name('finnish'), Fi)
        assert isinstance(Language.from_name('Finnish'), Fi)

    def test_hyphen_is_ignored(self):
        assert isinstance(Language.from_name('pt-br'), PtBr)
        assert isinstance(Language.from_name('PT-BR'), PtBr)

    def test_no_match(self):
        assert_raises_with_msg(ValueError, "No language with name 'no match' found.",
                               Language.from_name, 'no match')


if __name__ == '__main__':
    unittest.main()
