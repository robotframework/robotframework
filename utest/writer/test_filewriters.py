import unittest
from StringIO import StringIO

from robot.parsing import TestCaseFile
from robot.parsing.model import TestCaseTable
from robot.utils.asserts import assert_equals


class TestSpaceSeparatedWriter(unittest.TestCase):

    def test_end_of_line_whitespace_is_removed(self):
        output = StringIO()
        self._create_test_case_file().save(output=output)
        expected = '''
*** test case ***     some    and other
A test
                      A kw    an arg'''.strip()
        for exp, act in zip(expected.splitlines(), output.getvalue().splitlines()):
            assert_equals(repr(exp), repr(act))

    def _create_test_case_file(self):
        data = TestCaseFile(source='foo.txt')
        table = TestCaseTable(data)
        data.testcase_table = table
        table.set_header(['test case', 'some', 'and other'])
        test = table.add('A test')
        test.add_step(['A kw', 'an arg'])
        return data

