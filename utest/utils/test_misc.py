import re
import unittest

from robot.utils import (classproperty, parse_re_flags, plural_or_not, printable_name,
                         seq2str, test_or_task)
from robot.utils.asserts import assert_equal, assert_raises, assert_raises_with_msg


class TestSeg2Str(unittest.TestCase):

    def _verify(self, input, expected, **config):
        assert_equal(seq2str(input, **config), expected)

    def test_empty(self):
        for seq in [[], (), set()]:
            self._verify(seq, '')

    def test_one_or_more(self):
        for seq, expected in [(['One'], "'One'"),
                              (['1', '2'], "'1' and '2'"),
                              (['a', 'b', 'c', 'd'], "'a', 'b', 'c' and 'd'")]:
            self._verify(seq, expected)

    def test_non_ascii_unicode(self):
        self._verify(['hyvä', 'äiti', '🏆'], "'hyvä', 'äiti' and '🏆'")

    def test_ascii_bytes(self):
        self._verify([b'ascii'], "'ascii'")

    def test_non_ascii_bytes(self):
        self._verify([b'non-\xe4scii'], "'non-\\xe4scii'")

    def test_other_objects(self):
        self._verify([None, 1, True], "'None', '1' and 'True'")


class TestPrintableName(unittest.TestCase):

    def test_printable_name(self):
        for inp, exp in [('simple', 'Simple'),
                         ('ALLCAPS', 'ALLCAPS'),
                         ('name with spaces', 'Name With Spaces'),
                         ('more   spaces', 'More Spaces'),
                         ('  leading and trailing  ', 'Leading And Trailing'),
                         ('  12number34  ', '12number34'),
                         ('Cases AND spaces', 'Cases AND Spaces'),
                         ('under_Score_name', 'Under_Score_name'),
                         ('camelCaseName', 'CamelCaseName'),
                         ('with89numbers', 'With89numbers'),
                         ('with 89 numbers', 'With 89 Numbers'),
                         ('with 89_numbers', 'With 89_numbers'),
                         ('', '')]:
            assert_equal(printable_name(inp), exp)

    def test_printable_name_with_code_style(self):
        for inp, exp in [('simple', 'Simple'),
                         ('ALLCAPS', 'ALLCAPS'),
                         ('name with spaces', 'Name With Spaces'),
                         ('    more   spaces    ', 'More Spaces'),
                         ('under_score_name', 'Under Score Name'),
                         ('under__score and spaces', 'Under Score And Spaces'),
                         ('__leading and trailing_ __', 'Leading And Trailing'),
                         ('__12number34__', '12 Number 34'),
                         ('miXed_CAPS_nAMe', 'MiXed CAPS NAMe'),
                         ('with 89_numbers', 'With 89 Numbers'),
                         ('camelCaseName', 'Camel Case Name'),
                         ('mixedCAPSCamelName', 'Mixed CAPS Camel Name'),
                         ('camelCaseWithDigit1', 'Camel Case With Digit 1'),
                         ('teamX', 'Team X'),
                         ('name42WithNumbers666', 'Name 42 With Numbers 666'),
                         ('name42WITHNumbers666', 'Name 42 WITH Numbers 666'),
                         ('12more34numbers', '12 More 34 Numbers'),
                         ('2KW', '2 KW'),
                         ('KW2', 'KW 2'),
                         ('xKW', 'X KW'),
                         ('KWx', 'K Wx'),
                         (':KW', ':KW'),
                         ('KW:', 'KW:'),
                         ('foo-bar', 'Foo-bar'),
                         ('Foo-b:a;r!', 'Foo-b:a;r!'),
                         ('Foo-B:A;R!', 'Foo-B:A;R!'),
                         ('', '')]:
            assert_equal(printable_name(inp, code_style=True), exp)


class TestPluralOrNot(unittest.TestCase):

    def test_plural_or_not(self):
        for singular in [1, -1, (2,), ['foo'], {'key': 'value'}, 'x']:
            assert_equal(plural_or_not(singular), '')
        for plural in [0, 2, -2, 42,
                       (), [], {},
                       (1, 2, 3), ['a', 'b'], {'a': 1, 'b': 2},
                       '', 'xx', 'Hello, world!']:
            assert_equal(plural_or_not(plural), 's')


class TestTestOrTask(unittest.TestCase):

    def test_no_match(self):
        for inp in ['', 'No match', 'No {match}', '{No} {task} {match}']:
            assert_equal(test_or_task(inp, rpa=False), inp)
            assert_equal(test_or_task(inp, rpa=True), inp)

    def test_match(self):
        for test, task in [('test', 'task'),
                           ('Test', 'Task'),
                           ('TEST', 'TASK'),
                           ('tESt', 'tASk')]:
            inp = '{%s}' % test
            assert_equal(test_or_task(inp, rpa=False), test)
            assert_equal(test_or_task(inp, rpa=True), task)

    def test_multiple_matches(self):
        assert_equal(test_or_task('Contains {test}, {TEST} and {TesT}', False),
                     'Contains test, TEST and TesT')
        assert_equal(test_or_task('Contains {test}, {TEST} and {TesT}', True),
                     'Contains task, TASK and TasK')

    def test_test_without_curlies(self):
        for test, task in [('test', 'task'),
                           ('Test', 'Task'),
                           ('TEST', 'TASK'),
                           ('tESt', 'tASk')]:
            assert_equal(test_or_task(test, rpa=False), test)
            assert_equal(test_or_task(test, rpa=True), task)


class TestParseReFlags(unittest.TestCase):

    def test_parse(self):
        for inp, exp in [('DOTALL', re.DOTALL),
                         ('I', re.I),
                         ('IGNORECASE|dotall', re.IGNORECASE | re.DOTALL),
                         (' MULTILINE ', re.MULTILINE)]:
            assert_equal(parse_re_flags(inp), exp)

    def test_parse_empty(self):
        for inp in ['', None]:
            assert_equal(parse_re_flags(inp), 0)

    def test_parse_negative(self):
        for inp, exp_msg in [('foo', 'Unknown regexp flag: foo'),
                             ('IGNORECASE|foo', 'Unknown regexp flag: foo'),
                             ('compile', 'Unknown regexp flag: compile')]:
            assert_raises_with_msg(ValueError, exp_msg, parse_re_flags, inp)


class TestClassProperty(unittest.TestCase):

    def setUp(self):
        class Class:
            @classproperty
            def p(cls):
                assert cls is Class
                return 1
        self.cls = Class

    def test_get_from_class(self):
        assert self.cls.p == 1

    def test_get_from_instance(self):
        assert self.cls().p == 1

    def test_set_in_class_overrides(self):
        # This cannot be avoided without using metaclasses.
        self.cls.p = 2
        assert self.cls.p == 2
        assert self.cls().p == 2

    def test_set_in_instance_fails(self):
        assert_raises(AttributeError, setattr, self.cls(), 'p', 2)

    def test_cannot_have_setter(self):
        code = '''
class Class:
    @classproperty
    def p(cls):
        pass
    @p.setter
    def p(cls):
        pass
'''
        assert_raises_with_msg(TypeError, 'Setters are not supported.',
                               exec, code, globals())
        assert_raises_with_msg(TypeError, 'Setters are not supported.',
                               classproperty, lambda c: None, lambda c, v: None)

    def test_cannot_have_deleter(self):
        code = '''
class Class:
    @classproperty
    def p(cls):
        pass
    @p.deleter
    def p(cls):
        pass
'''
        assert_raises_with_msg(TypeError, 'Deleters are not supported.',
                               exec, code, globals())
        assert_raises_with_msg(TypeError, 'Deleters are not supported.',
                               classproperty, lambda c: None, None, lambda c, v: None)

    def test_doc(self):
        class Class(self.cls):
            @classproperty
            def p(cls):
                """Doc for p."""
            q = classproperty(lambda cls: None, doc='Doc for q.')
        assert_equal(Class.__dict__['p'].__doc__, 'Doc for p.')
        assert_equal(Class.__dict__['q'].__doc__, 'Doc for q.')


if __name__ == "__main__":
    unittest.main()
