import unittest

from robot.api import Language, Languages
from robot.conf.languages import En, Fi, PtBr, Th
from robot.utils.asserts import assert_equal, assert_not_equal, assert_raises_with_msg


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

    def test_name_without_docstring(self):
        class X(Language):
            pass
        X.__doc__ = None
        assert_equal(X().name, '')

    def test_all_standard_languages_have_code_and_name(self):
        for cls in Language.__subclasses__():
            lang = cls()
            assert lang.code
            assert lang.name

    def test_eq(self):
        assert_equal(Fi(), Fi())
        assert_equal(Language.from_name('fi'), Fi())
        assert_not_equal(Fi(), PtBr())

    def test_hash(self):
        assert_equal(hash(Fi()), hash(Fi()))
        assert_equal({Fi(): 'value'}[Fi()], 'value')

    def test_subclasses_dont_have_wrong_attributes(self):
        for cls in Language.__subclasses__():
            for attr in dir(cls):
                if not hasattr(Language, attr):
                    raise AssertionError(f"Language class '{cls}' has attribute "
                                         f"'{attr}' not found on the base class.")


class TestLanguageFromName(unittest.TestCase):

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


class TestLanguages(unittest.TestCase):

    def test_init(self):
        assert_equal(list(Languages()), [En()])
        assert_equal(list(Languages('fi')), [Fi(), En()])
        assert_equal(list(Languages(['fi'])), [Fi(), En()])
        assert_equal(list(Languages(['fi', PtBr()])), [Fi(), PtBr(), En()])

    def test_reset(self):
        langs = Languages(['fi'])
        langs.reset()
        assert_equal(list(langs), [En()])
        langs.reset('fi')
        assert_equal(list(langs), [Fi(), En()])
        langs.reset(['fi', PtBr()])
        assert_equal(list(langs), [Fi(), PtBr(), En()])

    def test_duplicates_are_not_added(self):
        langs = Languages(['Finnish', 'en', Fi(), 'pt-br'])
        assert_equal(list(langs), [Fi(), En(), PtBr()])
        langs.add_language('en')
        assert_equal(list(langs), [Fi(), En(), PtBr()])
        langs.add_language('th')
        assert_equal(list(langs), [Fi(), En(), PtBr(), Th()])


if __name__ == '__main__':
    unittest.main()
