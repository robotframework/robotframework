import inspect
import unittest
import re
from pathlib import Path

from robot.api import Language, Languages
from robot.conf.languages import En, Fi, PtBr, Th
from robot.errors import DataError
from robot.utils.asserts import (assert_equal, assert_not_equal, assert_raises,
                                 assert_raises_with_msg)


STANDARD_LANGUAGES = Language.__subclasses__()


class TestLanguage(unittest.TestCase):

    def test_one_part_code(self):
        assert_equal(Fi().code, 'fi')
        assert_equal(Fi.code, 'fi')

    def test_two_part_code(self):
        assert_equal(PtBr().code, 'pt-BR')
        assert_equal(PtBr.code, 'pt-BR')

    def test_name(self):
        assert_equal(Fi().name, 'Finnish')
        assert_equal(Fi.name, 'Finnish')
        assert_equal(PtBr().name, 'Brazilian Portuguese')
        assert_equal(PtBr.name, 'Brazilian Portuguese')

    def test_name_with_multiline_docstring(self):
        class X(Language):
            """Language Name

            Other lines are ignored.
            """
        assert_equal(X().name, 'Language Name')
        assert_equal(X.name, 'Language Name')

    def test_name_without_docstring(self):
        class X(Language):
            pass
        X.__doc__ = None
        assert_equal(X().name, '')
        assert_equal(X.name, '')

    def test_standard_languages_have_code_and_name(self):
        for cls in STANDARD_LANGUAGES:
            assert cls().code
            assert cls.code
            assert cls().name
            assert cls.name

    def test_standard_language_doc_formatting(self):
        added_in_rf60 = {'bg', 'bs', 'cs', 'de', 'en', 'es', 'fi', 'fr', 'hi',
                         'it', 'nl', 'pl', 'pt', 'pt-BR', 'ro', 'ru', 'sv',
                         'th', 'tr', 'uk', 'zh-CN', 'zh-TW'}
        for cls in STANDARD_LANGUAGES:
            doc = inspect.getdoc(cls)
            if cls.code in added_in_rf60:
                if doc != cls.name:
                    raise AssertionError(
                        f'Invalid docstring for {cls.name}. '
                        f'Expected only language name, got:\n{doc}'
                    )
            else:
                if not re.match(rf'{cls.name}\n\nNew in Robot Framework [\d.]+\.', doc):
                    raise AssertionError(
                        f'Invalid docstring for {cls.name}. '
                        f'Expected language name and "New in" note, got:\n{doc}'
                    )

    def test_code_and_name_of_Language_base_class_are_propertys(self):
        assert isinstance(Language.code, property)
        assert isinstance(Language.name, property)

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

    def test_bdd_prefixes(self):
        class X(Language):
            given_prefixes = ['List', 'is', 'default']
            when_prefixes = {}
            but_prefixes = ('but', 'any', 'iterable', 'works')
        assert_equal(X().bdd_prefixes, {'List', 'is', 'default',
                                        'but', 'any', 'iterable', 'works'})


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
        assert_equal(list(Languages(add_english=False)), [])
        assert_equal(list(Languages('fi', add_english=False)), [Fi()])
        assert_equal(list(Languages(['fi'], add_english=False)), [Fi()])
        assert_equal(list(Languages(['fi', PtBr()], add_english=False)), [Fi(), PtBr()])

    def test_init_with_custom_language(self):
        path = Path(__file__).absolute().parent / 'orcish_languages.py'
        cwd = Path('.').absolute()
        for lang in (path, path.relative_to(cwd),
                     str(path), str(path.relative_to(cwd)),
                     [str(path)], [path]):
            langs = Languages(lang, add_english=False)
            assert_equal([("Orcish Loud", "or-CLOU"), ("Orcish Quiet", "or-CQUI")],
                         [(v.name, v.code) for v in langs])

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
        langs.reset(add_english=False)
        assert_equal(list(langs), [])
        langs.reset('fi', add_english=False)
        assert_equal(list(langs), [Fi()])
        langs.reset(['fi', PtBr()], add_english=False)
        assert_equal(list(langs), [Fi(), PtBr()])

    def test_duplicates_are_not_added(self):
        langs = Languages(['Finnish', 'en', Fi(), 'pt-br'])
        assert_equal(list(langs), [Fi(), En(), PtBr()])
        langs.add_language('en')
        assert_equal(list(langs), [Fi(), En(), PtBr()])
        langs.add_language('th')
        assert_equal(list(langs), [Fi(), En(), PtBr(), Th()])

    def test_add_language_using_custom_module(self):
        path = Path(__file__).absolute().parent / 'orcish_languages.py'
        cwd = Path('.').absolute()
        for lang in [path, path.relative_to(cwd), str(path), str(path.relative_to(cwd))]:
            langs = Languages(add_english=False)
            langs.add_language(lang)
            assert_equal([("Orcish Loud", "or-CLOU"), ("Orcish Quiet", "or-CQUI")],
                         [(v.name, v.code) for v in langs])

    def test_add_language_using_invalid_custom_module(self):
        error = assert_raises(DataError, Languages().add_language, 'non_existing_a23l4j')
        assert_equal(error.message.split(':')[0],
                     "No language with name 'non_existing_a23l4j' found. "
                     "Importing language file 'non_existing_a23l4j' failed")

    def test_add_language_using_invalid_custom_module_as_Path(self):
        invalid = Path('non_existing_a23l4j')
        assert_raises_with_msg(DataError,
                               f"Importing language file '{invalid.absolute()}' failed: "
                               f"File or directory does not exist.",
                               Languages().add_language, invalid)

    def test_add_language_using_Language_instance(self):
        languages = Languages(add_english=False)
        to_add = [Fi(), PtBr(), Th()]
        for lang in to_add:
            languages.add_language(lang)
        assert_equal(list(languages), to_add)


if __name__ == '__main__':
    unittest.main()
