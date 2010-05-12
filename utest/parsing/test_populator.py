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

    def _assert_setting(self, setting_name, exp_value):
        assert_equals(getattr(self._datafile.setting_table, setting_name).value,
                      exp_value)

    def _start_table(self, name):
        return self._populator.start_table(name)

    def _add_row(self, row):
        self._populator.add(row)


if __name__ == '__main__':
    unittest.main()