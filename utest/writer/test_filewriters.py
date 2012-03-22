from __future__ import with_statement
import unittest
from StringIO import StringIO

from robot.parsing import TestCaseFile
from robot.parsing.model import TestCaseTable
from robot.utils.asserts import assert_equals
from robot.utils import ET, ETSource


def create_test_case_file():
    data = TestCaseFile(source='foo.txt')
    table = TestCaseTable(data)
    data.testcase_table = table
    table.set_header(['test case', 'some', 'and other'])
    test = table.add('A test')
    test.add_step(['A kw', 'an arg'])
    return data


class _WriterTestCase(unittest.TestCase):

    def _test_rows_are_not_split_if_there_are_headers(self, format='txt'):
        output = self._add_long_step_and_save(format)
        assert_equals(len(output.splitlines()), 4)

    def _add_long_step_and_save(self, format):
        data = create_test_case_file()
        data.testcase_table.tests[0].add_step(['A kw', '1', '2', '3', '4', '6', '7', '8'])
        output = StringIO()
        data.save(format=format, output=output)
        return output.getvalue().strip()


class TestSpaceSeparatedWriter(_WriterTestCase):

    def test_end_of_line_whitespace_is_removed(self):
        output = StringIO()
        create_test_case_file().save(output=output)
        expected = '''
*** test case ***     some    and other
A test
                      A kw    an arg'''.strip()
        for exp, act in zip(expected.splitlines(), output.getvalue().splitlines()):
            assert_equals(repr(exp), repr(act))

    def test_rows_are_not_split_if_there_are_headers(self):
        self._test_rows_are_not_split_if_there_are_headers()

    def test_configuring_number_of_separating_spaces(self):
        output = StringIO()
        create_test_case_file().save(output=output, txt_separating_spaces=8)
        expected = '''\
*** test case ***         some        and other
A test
                          A kw        an arg'''.strip()
        actual = output.getvalue().strip()
        assert_equals(expected.splitlines(), actual.splitlines())


class TestTsvWriter(_WriterTestCase):

    def test_rows_are_not_split_if_there_are_headers(self):
        try:
            import csv
        except ImportError:
            pass   # csv not available on IronPython 2.7
        else:
            self._test_rows_are_not_split_if_there_are_headers('tsv')


class TestHtmlWriter(_WriterTestCase):

    def test_rows_are_not_split_if_there_are_headers(self):
        output = self._add_long_step_and_save('html')
        with ETSource('\n'.join(output.splitlines()[1:])) as source:
            tree = ET.parse(source)
        lines = tree.findall('body/table/tr')
        assert_equals(len(lines), 4)
        for l in lines:
            cols = l.findall('td') or l.findall('th')
            assert_equals(len(cols), 9)


if __name__ == '__main__':
    unittest.main()
