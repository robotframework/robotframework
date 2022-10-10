import unittest

from os.path import abspath, dirname, join

from robot.api import Language, Languages
from robot.conf.languages import En, Fi, PtBr, Th
from robot.utils.asserts import assert_equal, assert_not_equal, assert_raises_with_msg, assert_true


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

    def test_init_without_default(self):
        assert_equal(list(Languages(add_default=False)), [])
        assert_equal(list(Languages('fi', add_default=False)), [Fi()])
        assert_equal(list(Languages(['fi'], add_default=False)), [Fi()])
        assert_equal(list(Languages(['fi', PtBr()], add_default=False)), [Fi(), PtBr()])

    def test_reset(self):
        langs = Languages(['fi'])
        langs.reset()
        assert_equal(list(langs), [En()])
        langs.reset('fi')
        assert_equal(list(langs), [Fi(), En()])
        langs.reset(['fi', PtBr()])
        assert_equal(list(langs), [Fi(), PtBr(), En()])

    def test_reset_with_default(self):
        langs = Languages(['fi'])
        langs.reset(add_default=False)
        assert_equal(list(langs), [])
        langs.reset('fi', add_default=False)
        assert_equal(list(langs), [Fi()])
        langs.reset(['fi', PtBr()], add_default=False)
        assert_equal(list(langs), [Fi(), PtBr()])

    def test_duplicates_are_not_added(self):
        langs = Languages(['Finnish', 'en', Fi(), 'pt-br'])
        assert_equal(list(langs), [Fi(), En(), PtBr()])
        langs.add_language('en')
        assert_equal(list(langs), [Fi(), En(), PtBr()])
        langs.add_language('th')
        assert_equal(list(langs), [Fi(), En(), PtBr(), Th()])

    def test_get_available_languages(self):
        languages = Languages.get_available_languages()
        self.assertIn(("en", En), languages.items())
        self.assertIn(("english", En), languages.items())
        self.assertIn(("fi", Fi), languages.items())
        self.assertIn(("finnish", Fi), languages.items())

    def test_import_language_module(self):
        data = join(abspath(dirname(__file__)), 'elvish_languages.py')
        languages = Languages.import_language_module(data)

        self.assertIn("elvsin", languages)
        self.assertIn("elvishsindarin", languages)
        self.assertIn("elvque", languages)
        self.assertIn("elvishquenya", languages)

        avail_languages = Languages.get_available_languages()

        self.assertIn("elvsin", avail_languages)
        self.assertIn("elvishsindarin", avail_languages)
        self.assertIn("elvque", avail_languages)
        self.assertIn("elvishquenya", avail_languages)

    def test_init_with_language_module(self):
        data = join(abspath(dirname(__file__)), 'orcish_languages.py')
        languages = [(v.name, v.code) for v in Languages(data)]
        self.assertIn(("Orcish Loud", "or-CLOU"), languages)
        self.assertIn(("Orcish Quiet", "or-CQUI"), languages)
        self.assertIn(("English", "en"), languages)


if __name__ == '__main__':
    unittest.main()
