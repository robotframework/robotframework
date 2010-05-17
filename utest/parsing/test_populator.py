import unittest

from robot.parsing.populator import Populator
from robot.parsing.newmodel import TestCaseFile
from robot.utils.asserts import assert_equals, assert_true, assert_false


class TestCaseFilePopulatingTest(unittest.TestCase):

    def setUp(self):
        self._datafile = TestCaseFile()
        self._path = '/path/to/source'
        self._populator = Populator(self._datafile, self._path)

    def test_creation(self):
        assert_equals(self._datafile.source, self._path)

    def test_starting_valid_table(self):
        for name in ['Test Cases', '  variables   ', 'K E Y WO R D S']:
            assert_true(self._start_table(name))

    def test_starting_invalid_table(self):
        assert_false(self._start_table('Per Se'))

    def test_adding_empty_row_should_not_fail(self):
        self._start_table('Settings')
        self._add_row([])

    def test_adding_settings(self):
        self._start_table('Settings')
        doc = 'This is doc'
        self._add_row(['Documentation', doc])
        setup = ['Keyword Name', 'Argument name']
        self._add_row(['S  uite SeTUp'] + setup)
        self._populator.eof()
        self._assert_setting('doc', doc)
        self._assert_setting('suite_setup', setup)

    def test_adding_variables(self):
        self._start_table('Variables')
        self._add_row(['${scalar}', 'value'])
        self._add_row(['@{list}', 'v1', 'v2'])
        self._add_row(['...', 'v3', 'v4'])
        self._populator.eof()
        assert_equals(len(self._datafile.variable_table.variables), 2)
        assert_equals(self._datafile.variable_table.variables[0].name, '${scalar}')

    def test_setting_in_multiple_rows(self):
        self._start_table('Settings')
        self._add_row(['Documentation', 'Part 1'])
        self._add_row(['...', 'Part 2'])
        self._populator.eof()
        self._assert_setting('doc', 'Part 1 Part 2')

    def test_adding_import(self):
        self._start_table('settings')
        self._populator.add(['Library', 'FooBarness'])
        self._populator.add(['Library', 'BarFooness'])
        self._populator.add(['Resource', 'QuuxNess.txt'])
        self._populator.add(['Variables', 'varzors.py'])
        self._populator.eof()
        assert_equals(len(self._datafile.setting_table.imports), 4)

    def test_test_case_populating(self):
        self._start_table('Test cases')
        self._populator.add(['My test name'])
        self._populator.add(['', 'No operation'])
        self._populator.add(['Another test'])
        self._populator.add(['', 'Log', 'quux'])
        self._populator.eof()
        assert_equals(len(self._datafile.testcase_table.tests), 2)
        test = self._datafile.testcase_table.tests[0]
        assert_equals(len(test.steps), 1)
        assert_equals(test.steps[0].keyword, 'No operation')
        test = self._datafile.testcase_table.tests[1]
        assert_equals(len(test.steps), 1)

    def test_case_name_and_first_step_on_same_row(self):
        self._start_table('Test cases')
        self._populator.add(['My test name', 'No Operation'])
        self._populator.eof()
        test = self._datafile.testcase_table.tests[0]
        assert_equals(len(test.steps), 1)

    def test_continuing_row_in_test(self):
        self._start_table('Test cases')
        self._populator.add(['My test name', 'Log Many', 'foo'])
        self._populator.add(['', '...', 'bar', 'quux'])
        self._populator.add(['Another test'])
        self._populator.add(['', 'Log Many', 'quux'])
        self._populator.add(['', '...', 'fooness'])
        self._populator.add(['', 'Log', 'barness'])
        self._populator.eof()
        test = self._datafile.testcase_table.tests[0]
        assert_equals(len(test.steps), 1)
        test = self._datafile.testcase_table.tests[1]
        assert_equals(len(test.steps), 2)

    def test_test_settings(self):
        self._start_table('Test cases')
        self._populator.add(['My test name'])
        self._populator.add(['', '[Documentation]', 'This is domumentation for the test case'])
        self._populator.add(['', '[  Tags  ]', 'ankka', 'kameli'])
        self._populator.add(['', '... ', 'aasi'])
        self._populator.add(['', 'Log', 'barness'])
        self._populator.eof()
        test = self._datafile.testcase_table.tests[0]
        assert_equals(len(test.steps), 1)
        assert_equals(test.doc.value, 'This is domumentation for the test case')
        assert_equals(test.tags.value, ['ankka', 'kameli', 'aasi'])

    def test_creating_user_keywords(self):
        self._start_table('Keywords')
        self._populator.add(['My User Keyword'])
        self._populator.add(['', '[Arguments]', '${foo}', '${bar}'])
        self._populator.add(['', 'Log Many', '${foo}'])
        self._populator.add(['', '...', 'bar'])
        self._populator.add(['', 'No Operation'])
        self._populator.add(['', '[Return]', 'ankka', 'kameli'])
        self._populator.eof()
        uk = self._datafile.keyword_table.keywords[0]
        assert_equals(len(uk.steps), 2)
        assert_equals(uk.args.value, ['${foo}', '${bar}'])
        assert_equals(uk.return_.value, ['ankka', 'kameli'])

    def _assert_setting(self, setting_name, exp_value):
        assert_equals(getattr(self._datafile.setting_table, setting_name).value,
                      exp_value)

    def _start_table(self, name):
        return self._populator.start_table(name)

    def _add_row(self, row):
        self._populator.add(row)


if __name__ == '__main__':
    unittest.main()
