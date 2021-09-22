import unittest

from robot.utils.asserts import assert_equal
from robot.utils import printable_name, seq2str, roundup, plural_or_not, test_or_task


class TestRoundup(unittest.TestCase):

    def test_basics(self):
        for number in range(1000):
            for extra in range(5):
                extra /= 10.0
                assert_equal(roundup(number + extra), number, +extra)
                assert_equal(roundup(number - extra), number, -extra)
            assert_equal(roundup(number + 0.5), number+1)

    def test_negative(self):
        for number in range(1000):
            number *= -1
            for extra in range(5):
                extra /= 10.0
                assert_equal(roundup(number + extra), number)
                assert_equal(roundup(number - extra), number)
            assert_equal(roundup(number - 0.5), number-1)

    def test_ndigits_below_zero(self):
        assert_equal(roundup(7, -1), 10)
        assert_equal(roundup(77, -1), 80)
        assert_equal(roundup(123, -2), 100)
        assert_equal(roundup(-1234, -2), -1200)
        assert_equal(roundup(9999, -2), 10000)

    def test_ndigits_above_zero(self):
        assert_equal(roundup(0.1234, 1), 0.1)
        assert_equal(roundup(0.9999, 1), 1.0)
        assert_equal(roundup(0.9876, 3), 0.988)

    def test_round_even_up(self):
        assert_equal(roundup(0.5), 1)
        assert_equal(roundup(5, -1), 10)
        assert_equal(roundup(500, -3), 1000)
        assert_equal(roundup(0.05, 1), 0.1)
        assert_equal(roundup(0.49951, 3), 0.5)

    def test_round_even_down_when_negative(self):
        assert_equal(roundup(-0.5), -1)
        assert_equal(roundup(-5, -1), -10)
        assert_equal(roundup(-5.0, -1), -10)
        assert_equal(roundup(-500, -3), -1000)
        assert_equal(roundup(-0.05, 1), -0.1)
        assert_equal(roundup(-0.49951, 3), -0.5)

    def test_return_type(self):
        for n in [1, 1000, 0.1, 0.001]:
            for d in [-3, -2, -1, 0, 1, 2, 3]:
                assert_equal(type(roundup(n, d)), float if d > 0 else int)
                assert_equal(type(roundup(n, d, return_type=int)), int)
                assert_equal(type(roundup(n, d, return_type=float)), float)

    def test_problems(self):
        assert_equal(roundup(59.85, 1), 59.9)    # This caused #2872
        assert_equal(roundup(1.15, 1), 1.1)      # 1.15 is actually 1.49999..


class TestSeg2Str(unittest.TestCase):

    def _verify(self, input, expected, **config):
        assert_equal(seq2str(input, **config), expected)

    def test_empty(self):
        for seq in [[], (), set()]:
            self._verify(seq, '')

    def test_one_or_more(self):
        for seq, expected in [(['One'], "'One'"),
                              (['1', '2'], "'1' and '2'"),
                              (['a', 'b', 'c', 'd'], "'a', 'b', 'c' and 'd'"),
                              ([u'Unicode', u'ASCII'], "'Unicode' and 'ASCII'")]:
            self._verify(seq, expected)

    def test_non_ascii_unicode(self):
        self._verify([u'hyv\xe4'], u"'hyv\xe4'")

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
            assert_equal(test_or_task(inp), inp)
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


if __name__ == "__main__":
    unittest.main()
