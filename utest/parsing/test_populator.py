import unittest
import os
from StringIO import StringIO

from robot.parsing.populator import TestDataPopulator
from robot.parsing.newmodel import TestCaseFile
from robot.utils.asserts import assert_equals, assert_true, assert_false

from robot.output import LOGGER
LOGGER.disable_automatic_console_logger()
LOGGER.disable_message_cache()


class _MockLogger(object):
    def __init__(self):
        self._output = StringIO()

    def message(self, msg):
        self._output.write(msg.message)

    def value(self):
        return self._output.getvalue()


class TestCaseFilePopulatingTest(unittest.TestCase):

    def setUp(self):
        self._datafile = TestCaseFile()
        self._datafile.source = '/path/to/source.txt'
        self._populator = TestDataPopulator(self._datafile)
        self._logger = _MockLogger()
        LOGGER.register_logger(self._logger)

    def tearDown(self):
        LOGGER.unregister_logger(self._logger)

    def test_starting_valid_table(self):
        for name in ['Test Cases', '  variables   ', 'K E Y WO R D S']:
            assert_true(self._start_table(name))

    def test_starting_invalid_table(self):
        assert_false(self._start_table('Per Se'))

    def test_adding_empty_row_should_not_fail(self):
        self._create_table('Settings', [[]])

    def test_adding_settings(self):
        doc = 'This is doc'
        setup_name, setup_args = 'Keyword Name', ['a1', 'a2']
        self._create_table('Settings', [['Documentation', doc],
                                        ['S  uite SeTUp'] + [setup_name] + setup_args])
        self._assert_setting('doc', doc)
        self._assert_fixture('suite_setup', setup_name, setup_args)

    def test_invalid_settings(self):
        self._create_table('Settings', [['In valid', 'val ue']])
        assert_equals(self._logger.value(), "Invalid setting 'In valid' in setting table.")

    def test_adding_import(self):
        self._create_table('settings', [['Library', 'FooBarness'],
                                        ['Library', 'BarFooness', 'arg1', 'arg2'],
                                        ['Resource', 'QuuxNess.txt'],
                                        ['Variables', 'varzors.py']])
        assert_equals(len(self._datafile.setting_table.imports), 4)
        self._assert_import(0, 'FooBarness', [])
        self._assert_import(1, 'BarFooness', ['arg1', 'arg2'])
        self._assert_import(2, 'QuuxNess.txt', [])
        self._assert_import(3, 'varzors.py', [])

    def test_suite_metadata(self):
        self._create_table('settings', [['Meta: Foon:ess', 'Barness'],
                                        ['Metadata', 'Quux', 'Value']])
        self._assert_meta(0, 'Foon:ess', 'Barness')
        self._assert_meta(1, 'Quux', 'Value')

    def test_adding_variables(self):
        self._create_table('Variables', [['${scalar}', 'value'],
                                         ['@{list}', 'v1', 'v2'],
                                         ['...', 'v3', 'v4']])
        assert_equals(len(self._datafile.variable_table.variables), 2)
        assert_equals(self._datafile.variable_table.variables[0].name, '${scalar}')

    def test_setting_in_multiple_rows(self):
        self._create_table('Settings', [['Documentation', 'Part 1'],
                                        ['...', 'Part 2']])
        self._assert_setting('doc', 'Part 1 Part 2')

    def test_test_case_populating(self):
        self._create_table('Test cases', [['My test name'],
                                          ['', 'No operation'],
                                          ['Another test'],
                                          ['', 'Log', 'quux']])
        assert_equals(len(self._datafile.testcase_table.tests), 2)
        test = self._first_test()
        assert_equals(len(test.steps), 1)
        assert_equals(test.steps[0].keyword, 'No operation')
        assert_equals(len(self._first_test().steps), 1)

    def test_case_name_and_first_step_on_same_row(self):
        self._create_table('Test cases', [['My test name', 'No Operation']])
        assert_equals(len(self._first_test().steps), 1)

    def test_continuing_row_in_test(self):
        self._create_table('Test cases', [['My test name', 'Log Many', 'foo'],
                                          ['', '...', 'bar', 'quux'],
                                          ['Another test'],
                                          ['', 'Log Many', 'quux'],
                                          ['', '...', 'fooness'],
                                          ['', 'Log', 'barness']])
        assert_equals(len(self._first_test().steps), 1)
        assert_equals(len(self._nth_test(2).steps), 2)

    def test_for_loop(self):
        self._create_table('Test cases', [['For loop test'],
                                          ['', ':FOR', '${i}', 'IN', '@{list}'],
                                          ['', '', 'Log', '${i}']])
        assert_equals(len(self._first_test().steps), 1)
        for_loop = self._first_test().steps[0]
        assert_equals(len(for_loop.steps), 1)
        assert_true(not for_loop.range)
        assert_equals(for_loop.vars, ['${i}'])
        assert_equals(for_loop.values, ['@{list}'])

    def test_in_range_for_loop(self):
        self._create_table('Test cases', [['For loop test'],
                                          ['', 'Log', 'Before FOR'],
                                          ['', ': for', '${i}', '${j}', 'IN RANGE', '10'],
                                          ['', '', 'Log', '${i}'],
                                          ['', '', 'Fail', '${j}'],
                                          ['', 'Log', 'Outside FOR']])
        assert_equals(len(self._first_test().steps), 3)
        for_loop = self._first_test().steps[1]
        assert_equals(len(for_loop.steps), 2)
        assert_true(for_loop.range)
        assert_equals(for_loop.vars, ['${i}', '${j}'])

    def test_malicious_for_loop(self):
        self._create_table('Test cases', [['Malicious for loop test'],
                                          ['', 'Log', 'Before FOR'],
                                          ['#', 'Log', 'Before FOR'],
                                          ['', '::::   fOr', '${i}', 'IN', '10', '20'],
                                          ['#', '...', 'No operation'],
                                          ['', '...', '30', '40'],
                                          ['', '...', '50', '60'],
                                          ['', '', 'Log Many', '${i}'],
                                          ['', '', '...', '${i}'],
                                          ['', '...', '${i}'],
                                          ['', 'Log', 'Outside FOR']])
        assert_equals(len(self._first_test().steps), 3)
        for_loop = self._first_test().steps[1]
        assert_equals(len(for_loop.steps), 1)
        assert_true(not for_loop.range)
        assert_equals(for_loop.vars, ['${i}'])
        assert_equals(for_loop.values, ['10', '20', '30', '40', '50', '60'])

    def test_test_settings(self):
        doc = 'This is domumentation for the test case'
        self._create_table('Test cases', [['My test name'],
                                          ['', '[Documentation]', doc],
                                          ['', '[  Tags  ]', 'ankka', 'kameli'],
                                          ['', '... ', 'aasi'],
                                          ['', 'Log', 'barness']])
        test = self._first_test()
        assert_equals(len(test.steps), 1)
        assert_equals(test.doc.value, doc)
        assert_equals(test.tags.value, ['ankka', 'kameli', 'aasi'])

    def test_invalid_test_settings(self):
        self._create_table('Test cases', [['My test name'],
                                          ['', '[Aasi]']])
        assert_equals(self._logger.value(), "Invalid setting '[Aasi]' in test case 'My test name'.")

    def test_invalid_keyword_settings(self):
        self._create_table('Keywords', [['My User Keyword'],
                                        ['', '[ank ka]']])
        assert_equals(self._logger.value(), "Invalid setting '[ank ka]' in keyword 'My User Keyword'.")

    def test_creating_user_keywords(self):
        self._create_table('Keywords', [['My User Keyword'],
                                        ['', '[Arguments]', '${foo}', '${bar}'],
                                        ['', 'Log Many', '${foo}'],
                                        ['', '...', 'bar'],
                                        ['', 'No Operation'],
                                        ['', '[Return]', 'ankka', 'kameli']])
        uk = self._nth_uk(0)
        assert_equals(len(uk.steps), 2)
        assert_equals(uk.args.value, ['${foo}', '${bar}'])
        assert_equals(uk.return_.value, ['ankka', 'kameli'])

    def test_comment_handling(self):
        self._create_table('Keywords', [['#Commented row'],
                                        ['', '# Another Commented row'],
                                        ['My User Keyword', '#End', 'of', 'row comment'],
                                        ['', '[Arguments]', '${foo}', '${bar}'],
                                        ['', 'Log Many', '${foo}'],
                                        ['', '# Commented row inside kw'],
                                        ['', '...', 'bar'],
                                        ['', 'No Operation'],
                                        ['', '[Return]', 'ankka', 'kameli']])
        uk = self._nth_uk(0)
        assert_equals(len(uk.steps), 2)
        assert_equals(uk.args.value, ['${foo}', '${bar}'])
        assert_equals(uk.return_.value, ['ankka', 'kameli'])

    def test_curdir_handling(self):
        self._create_table('Test cases', [['My test name'],
                                          ['', 'Log', '${CURDIR}']])
        assert_equals(self._first_test().steps[0].args,
                      [os.path.dirname(self._datafile.source)])

    def test_turn_off_curdir_handling(self):
        from robot.parsing import populator
        populator.PROCESS_CURDIR = False
        self.setUp()
        self._create_table('Test cases', [['My test name'],
                                          ['', 'Log', '${CURDIR}']])
        assert_equals(self._first_test().steps[0].args, ['${CURDIR}'])
        populator.PROCESS_CURDIR = True

    def test_whitespace_is_ignored(self):
        self._create_table('Test Cases', [['My   test'],
                                          [' ', '[Tags]', 'foo', '  \t  '],
                                          ['  '],
                                          [ '\t'],
                                          ['', 'Log Many', '', 'argh']])
        test = self._first_test()
        assert_equals(test.name, 'My test')
        self._number_of_steps_should_be(test, 1)
        assert_equals(test.tags.value, ['foo'])

    def _assert_setting(self, setting_name, exp_value):
        assert_equals(self._setting_with(setting_name).value, exp_value)

    def _assert_meta(self, index, exp_name, exp_value):
        meta = self._setting_with('metadata')[index]
        assert_equals(meta.name, exp_name)
        assert_equals(meta.value, exp_value)

    def _setting_with(self, name):
        return getattr(self._datafile.setting_table, name)

    def _assert_fixture(self, fixture_name, exp_name, exp_args):
        fixture = self._setting_with(fixture_name)
        self._assert_name_and_args(fixture, exp_name, exp_args)

    def _assert_import(self, index, exp_name, exp_args):
        imp = self._datafile.setting_table.imports[index]
        self._assert_name_and_args(imp, exp_name, exp_args)

    def _assert_name_and_args(self, item, exp_name, exp_args):
        assert_equals(item.name, exp_name)
        assert_equals(item.args, exp_args)

    def _start_table(self, name):
        return self._populator.start_table(name)

    def _create_table(self, name, rows):
        self._start_table(name)
        for r  in rows:
            self._populator.add(r)
        self._populator.eof()

    def _nth_test(self, index):
        return self._datafile.testcase_table.tests[index-1]

    def _first_test(self):
        return self._nth_test(1)

    def _nth_uk(self, index):
        return self._datafile.keyword_table.keywords[index]

    def _number_of_steps_should_be(self, test, expected_steps):
        assert_equals(len(test.steps), expected_steps)


if __name__ == '__main__':
    unittest.main()
