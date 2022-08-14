import unittest

from robot.api import Language
from robot.conf.languages import Fi, PtBr
from robot.utils.asserts import assert_equal, assert_raises_with_msg


class TestLanguage(unittest.TestCase):

    def test_one_part_code(self):
        assert_equal(Fi().code, 'fi')

    def test_two_part_code(self):
        assert_equal(PtBr().code, 'pt-BR')

    def test_name(self):
        assert_equal(Fi().name, 'Finnish')
        assert_equal(PtBr().name, 'Brazilian Portuguese')

    def test_name_with_multiline_docstring(self):
        class X(Language):
            """Language Name

            Other lines are ignored.
            """
        assert_equal(X().name, 'Language Name')


class TestFromName(unittest.TestCase):

    def test_code(self):
        assert isinstance(Language.from_name('fi'), Fi)
        assert isinstance(Language.from_name('FI'), Fi)

    def test_two_part_code(self):
        assert isinstance(Language.from_name('pt-BR'), PtBr)
        assert isinstance(Language.from_name('PTBR'), PtBr)

    def test_name(self):
        assert isinstance(Language.from_name('finnish'), Fi)
        assert isinstance(Language.from_name('Finnish'), Fi)

    def test_multi_part_name(self):
        assert isinstance(Language.from_name('Brazilian Portuguese'), PtBr)
        assert isinstance(Language.from_name('brazilianportuguese'), PtBr)

    def test_no_match(self):
        assert_raises_with_msg(ValueError, "No language with name 'no match' found.",
                               Language.from_name, 'no match')


if __name__ == '__main__':
    unittest.main()
