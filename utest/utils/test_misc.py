import io
import sys
import unittest

from robot.utils import IRONPYTHON, PYTHON
from robot.utils.asserts import assert_equals, assert_false, assert_raises
from robot.utils.misc import getdoc, isatty, printable_name, seq2str


class TestMiscUtils(unittest.TestCase):

    def test_seq2str(self):
        for seq, expected in [((), ''), ([], ''), (set(), ''),
                              (['One'], "'One'"),
                              (['1', '2'], "'1' and '2'"),
                              (['a', 'b', 'c', 'd'], "'a', 'b', 'c' and 'd'")]:
            assert_equals(seq2str(seq), expected)

    def test_printable_name(self):
        for inp, exp in [('simple', 'Simple'),
                         ('ALLCAPS', 'ALLCAPS'),
                         ('name with spaces', 'Name With Spaces'),
                         ('more   spaces', 'More Spaces'),
                         ('Cases AND spaces', 'Cases AND Spaces'),
                         ('under_Score_name', 'Under_Score_name'),
                         ('camelCaseName', 'CamelCaseName'),
                         ('with89numbers', 'With89numbers'),
                         ('with 89 numbers', 'With 89 Numbers'),
                         ('', '')]:
            assert_equals(printable_name(inp), exp)

    def test_printable_name_with_code_style(self):
        for inp, exp in [('simple', 'Simple'),
                         ('ALLCAPS', 'ALLCAPS'),
                         ('under_score_name', 'Under Score Name'),
                         ('under_score and spaces', 'Under Score And Spaces'),
                         ('miXed_CAPS_nAMe', 'MiXed CAPS NAMe'),
                         ('camelCaseName', 'Camel Case Name'),
                         ('camelCaseWithDigit1', 'Camel Case With Digit 1'),
                         ('name42WithNumbers666', 'Name 42 With Numbers 666'),
                         ('12more34numbers', '12 More 34 Numbers'),
                         ('mixedCAPSCamelName', 'Mixed CAPS Camel Name'),
                         ('foo-bar', 'Foo-bar'),
                         ('', '')]:
            assert_equals(printable_name(inp, code_style=True), exp)


class TestIsATty(unittest.TestCase):

    def test_with_stdout(self):
        # file class based in PY2, io module based in PY3
        assert_equals(isatty(sys.__stdout__), sys.__stdout__.isatty())

    def test_with_io(self):
        with io.StringIO() as stream:
            assert_false(isatty(stream))
            wrapper = io.TextIOWrapper(stream)
            assert_false(isatty(wrapper))

    def test_with_detached_io_buffer(self):
        with io.StringIO() as stream:
            wrapper = io.TextIOWrapper(stream)
            if sys.version_info >= (2, 7):
                wrapper.detach()
                exc_type = ValueError if PYTHON else AttributeError
            else:
                wrapper.buffer = None
                exc_type = AttributeError
            assert_raises(exc_type, wrapper.isatty)
            assert_false(isatty(wrapper))


class TestGetdoc(unittest.TestCase):

    def test_no_doc(self):
        def func():
            pass
        assert_equals(getdoc(func), '')

    def test_one_line_doc(self):
        def func():
            """My documentation."""
        assert_equals(getdoc(func), 'My documentation.')

    def test_multiline_doc(self):
        class Class:
            """My doc.

            In multiple lines.
            """
        assert_equals(getdoc(Class), 'My doc.\n\nIn multiple lines.')
        assert_equals(getdoc(Class), getdoc(Class()))

    def test_non_ascii_doc_in_utf8(self):
        def func():
            """Hyv\xc3\xa4 \xc3\xa4iti!"""
        expected = u'Hyv\xe4 \xe4iti!' \
            if not IRONPYTHON else u'Hyv\xc3\xa4 \xc3\xa4iti!'
        assert_equals(getdoc(func), expected)

    def test_non_ascii_doc_not_in_utf8(self):
        def func():
            """Hyv\xe4 \xe4iti!"""
        expected = 'Hyv\\xe4 \\xe4iti!' \
            if not IRONPYTHON else u'Hyv\xe4 \xe4iti!'
        assert_equals(getdoc(func), expected)

    def test_unicode_doc(self):
        class Class:
            def meth(self):
                u"""Hyv\xe4 \xe4iti!"""
        assert_equals(getdoc(Class.meth), u'Hyv\xe4 \xe4iti!')
        assert_equals(getdoc(Class.meth), getdoc(Class().meth))


if __name__ == "__main__":
    unittest.main()
