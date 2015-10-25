import unittest

from robot.output import LOGGER
from robot.parsing.model import TestCaseFile
from robot.parsing.populators import FromFilePopulator, DataRow, FromDirectoryPopulator
from robot.utils import StringIO, is_string
from robot.utils.asserts import assert_equals, assert_true, assert_false


LOGGER.unregister_console_logger()


class _MockLogger(object):
    def __init__(self):
        self._output = StringIO()

    def message(self, msg):
        self._output.write(msg.message)

    def value(self):
        return self._output.getvalue()


class FromDirectoryPopulatorTest(unittest.TestCase):

    def test_included_suites_with_dot(self):
        create_included_suites = FromDirectoryPopulator()._create_included_suites
        for inp, exp in [([], []),
                         (['foo'], ['foo']),
                         (['bar.zoo'], ['bar.zoo', 'zoo']),
                         (['1.2.3', 'x.y', 'z'],
                          ['1.2.3', '2.3', '3', 'x.y', 'y', 'z'])]:
            assert_equals(list(create_included_suites(inp)), exp)


class _PopulatorTest(unittest.TestCase):

    def setUp(self):
        self._datafile = TestCaseFile()
        self._datafile.directory = '/path/to'
        self._populator = FromFilePopulator(self._datafile)
        self._logger = _MockLogger()
        LOGGER.disable_message_cache()
        LOGGER.register_logger(self._logger)

    def tearDown(self):
        LOGGER.unregister_logger(self._logger)

    def _assert_no_parsing_errors(self):
        assert_true(self._logger.value() == '', self._logger.value())

    def _start_table(self, name):
        if is_string(name):
            name = [name]
        return self._populator.start_table(name)

    def _create_table(self, name, rows, eof=True):
        self._start_table(name)
        for r in rows:
            self._populator.add(r)
        if eof:
            self._populator.eof()

    def _assert_setting(self, name, exp_value, exp_comment=None):
        setting = self._setting_with(name)
        assert_equals(setting.value, exp_value)
        self._assert_comment(setting, exp_comment)

    def _assert_fixture(self, fixture_name, exp_name, exp_args, exp_comment=None):
        fixture = self._setting_with(fixture_name)
        self._assert_name_and_args(fixture, exp_name, exp_args)
        self._assert_comment(fixture, exp_comment)

    def _assert_import(self, index, exp_name, exp_args, exp_comment=None):
        imp = self._datafile.setting_table.imports[index]
        self._assert_name_and_args(imp, exp_name, exp_args)
        self._assert_comment(imp, exp_comment)

    def _assert_name_and_args(self, item, exp_name, exp_args):
        assert_equals(item.name, exp_name)
        assert_equals(item.args, exp_args)

    def _assert_meta(self, index, exp_name, exp_value, exp_comment=None):
        meta = self._setting_with('metadata')[index]
        assert_equals(meta.name, exp_name)
        assert_equals(meta.value, exp_value)
        self._assert_comment(meta, exp_comment)

    def _assert_tags(self, tag_name, exp_value):
        tag = self._setting_with(tag_name)
        assert_equals(tag.value, exp_value)

    def _assert_variable(self, index, exp_name, exp_value, exp_comment=[]):
        var = self._datafile.variable_table.variables[index]
        assert_equals(var.name, exp_name)
        assert_equals(var.value, exp_value)
        self._assert_comment(var, exp_comment)

    def _assert_comment(self, item, exp_comment):
        if exp_comment:
            assert_equals(item.comment.as_list(), exp_comment)

    def _setting_with(self, name):
        return getattr(self._datafile.setting_table, name)

    def _nth_test(self, index):
        return self._datafile.testcase_table.tests[index-1]

    def _first_test(self):
        return self._nth_test(1)

    def _nth_uk(self, index):
        return self._datafile.keyword_table.keywords[index-1]

    def _number_of_steps_should_be(self, test, expected_steps):
        assert_equals(len(test.steps), expected_steps)


class TablePopulatorTest(_PopulatorTest):

    def test_starting_valid_table(self):
        for name in ['Test Cases', '  variables   ', 'K E Y WO R D S']:
            assert_true(self._start_table(name))

    def test_table_headers(self):
        header_list = ['seTTINGS', 'header', 'again']
        self._create_table(header_list,[])
        setting_table = self._datafile.setting_table
        assert_equals(setting_table.header, header_list)
        assert_equals(setting_table.name, header_list[0])

    def test_starting_invalid_table(self):
        assert_false(self._start_table('Per Se'))

    def test_adding_empty_row_should_not_fail(self):
        self._create_table('Settings', [[]])

    def test_curdir_handling(self):
        self._create_table('Test cases', [['My test name'],
                                          ['', 'Log', '${CURDIR}']])
        assert_equals(self._first_test().steps[0].args,
                      [self._datafile.directory])

    def test_turn_off_curdir_handling(self):
        from robot.parsing import populators
        populators.PROCESS_CURDIR = False
        self.setUp()
        self._create_table('Test cases', [['My test name'],
                                          ['', 'Log', '${CURDIR}']])
        assert_equals(self._first_test().steps[0].args, ['${CURDIR}'])
        populators.PROCESS_CURDIR = True

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

    def test_escaping_empty_cells(self):
        self._create_table('Settings', [['Documentation', '\\']],)
        self._assert_setting('doc', '')
        self._create_table('Test cases', [['test',
                                           '', 'Log Many', 'foo', '\\']],)
        assert_equals(self._first_test().steps[0].args, ['Log Many', 'foo', ''])

    def test_populator_happy_path_workflow(self):
        self._create_table('settings', [['Library', 'FooBarness']], eof=False)
        self._create_table('Variables', [['${scalar}', 'value']], eof=False)
        self._create_table('Test cases', [['My test name'],
                                          ['', 'Log', 'quux']], eof=False)
        self._create_table('More cases', [['My other test name'],
                                          ['', 'Log', 'foox']], eof=False)
        self._create_table('Keywords', [['My User Keyword'],
                                        ['', 'Foo', 'Bar']], eof=False)
        self._populator.eof()
        self._assert_import(0, 'FooBarness', [])
        assert_equals(len(self._datafile.variable_table.variables), 1)
        assert_equals(len(self._datafile.testcase_table.tests), 1)
        assert_equals(len(self._nth_uk(1).steps), 1)


class SettingTablePopulatingTest(_PopulatorTest):

    def test_testcasefile_settings(self):
        self._try_testcasefile_settings_with_postfix('')

    def test_testcasefile_settings_with_colon(self):
        self._try_testcasefile_settings_with_postfix(':')

    def test_testcasefile_settings_with_colon_and_spaces(self):
        self._try_testcasefile_settings_with_postfix('  :  ')

    def _try_testcasefile_settings_with_postfix(self, postfix):
        doc = 'This is doc'
        template = 'Foo'
        more_doc = 'smore'
        force_tags = 'force'
        more_tags = 'more tagness'
        even_more_tags = 'even more'
        default_tags = 'default'
        setup_name, setup_args = 'Keyword Name', ['a1', 'a2']
        table = [['Documentation', doc],
                 ['S  uite Tear Down'] + [setup_name],
                 ['S  uite SeTUp'] + [setup_name] + setup_args,
                 ['S  uite teardown'] + setup_args,
                 ['Doc um entati on', more_doc],
                 ['force tags', force_tags],
                 ['Default tags', default_tags],
                 ['FORCETAGS', more_tags],
                 ['test timeout', '1s'],
                 ['De Fault TAGS', more_tags, even_more_tags],
                 ['test timeout', 'timeout message'],
                 ['test timeout', more_doc],
                 ['test template', template]
                ]
        self._postfix_settings(table, postfix)
        self._create_table('Settings', table)
        self._assert_setting('doc', doc + ' ' + more_doc)
        self._assert_fixture('suite_setup', setup_name, setup_args)
        self._assert_fixture('suite_teardown', setup_name, setup_args)
        self._assert_tags('default_tags', [default_tags, more_tags, even_more_tags])
        self._assert_tags('force_tags', [force_tags, more_tags])
        timeout = self._setting_with('test_timeout')
        assert_equals(timeout.value, '1s')
        assert_equals(timeout.message, 'timeout message '+more_doc)
        self._assert_setting('test_template', template)

    def _postfix_settings(self, table, postfix):
        for setting in table:
            setting[0] = setting[0]+postfix

    def test_imports(self):
        self._create_table('settings', [['Library', 'FooBarness'],
                                        ['Library', 'BarFooness', 'arg1', 'arg2'],
                                        ['Resource', 'QuuxNess.txt'],
                                        ['Variables', 'varzors.py']])
        assert_equals(len(self._datafile.setting_table.imports), 4)
        self._assert_import(0, 'FooBarness', [])
        self._assert_import(1, 'BarFooness', ['arg1', 'arg2'])
        self._assert_import(2, 'QuuxNess.txt', [])
        self._assert_import(3, 'varzors.py', [])

    def test_free_suite_metadata(self):
        self._create_table('settings', [['Meta: Foon:ess', 'Barness'],
                                        ['Metadata', 'Quux', 'Value']])
        self._assert_meta(0, 'Foon:ess', 'Barness')
        self._assert_meta(1, 'Quux', 'Value')

    def test_line_continuation(self):
         self._create_table('Settings', [['Documentation', 'doc'],
                                         ['...'],
                                         ['...', 'in multiple lines'],
                                         ['Force Tags', 'one', 'two'],
                                         ['...'],
                                         ['', '...', 'three']
                                        ])
         self._assert_setting('doc', 'doc\\n\\nin multiple lines')
         self._assert_setting('force_tags', ['one', 'two', 'three'])

    def test_invalid_settings(self):
        self._create_table('Settings', [['In valid', 'val ue']])
        assert_equals(self._logger.value(), "Error in file 'None': "
                                            "Non-existing setting 'In valid'.")

    def test_continuing_in_the_begining_of_the_table(self):
        self._create_table('Settings', [['...']])
        assert_equals(self._logger.value(), "Error in file 'None': "
                                            "Non-existing setting '...'.")


class DocumentationCatenationTest(_PopulatorTest):

    def test_multiple_cells_are_catenated_with_space(self):
        self._assert_doc([['doc', 'in two cells']],
                           'doc in two cells')

    def test_multiple_rows_are_catenated_with_newline(self):
        self._assert_doc([['doc'], ['...', 'in two lines']],
                         'doc\\nin two lines')

    def test_newline_is_not_added_if_it_already_exists(self):
        self._assert_doc([['doc\\n'], ['in two lines']],
                         'doc\\nin two lines')

    def test_newline_is_not_added_if_it_already_exists2(self):
        self._assert_doc([['doc\\\\n'], ['in multiple\\\\\\n'], ['lines']],
                         'doc\\\\n\\nin multiple\\\\\\nlines')

    def test_backslash_escapes_newline_adding(self):
        self._assert_doc([['doc\\'], ['in two lines']],
                         'doc\\ in two lines')

    def test_backslash_escapes_newline_adding2(self):
        self._assert_doc([['doc\\\\'], ['in multiple\\\\\\', 'lines']],
                          'doc\\\\\\nin multiple\\\\\\ lines')

    def test_documentation_defined_multiple_times(self):
        self._create_table('Settings', [['Documentation', 'some doc'],
                                        ['Documentation', 'other doc'],
                                         ['...', 'third line']])
        self._assert_setting('doc', 'some doc other doc\\nthird line')

    def _assert_doc(self, doc_lines, expected):
        doc_lines = [['...'] + line for line in doc_lines]
        self._create_table('Settings', [['Documentation']] + doc_lines)
        self._assert_setting('doc', expected)


class MetadataCatenationTest(_PopulatorTest):

    def test_value_on_many_cells_is_catenated_with_spaces(self):
        self._assert_metadata_value([['value', 'in', 'cells']],
                                      'value in cells')

    def test_value_on_many_lines_is_catenated_with_newlines(self):
        self._assert_metadata_value([['value'], ['in'], ['lines']],
                                      'value\\nin\\nlines')

    def _assert_metadata_value(self, doc_lines, expected):
        value_lines = [['...'] + line for line in doc_lines]
        self._create_table('Settings', [['Metadata', 'metaname']] + value_lines)
        self._assert_meta(0, 'metaname', expected)


class VariableTablePopulatingTest(_PopulatorTest):

    def test_populating_variables(self):
        self._create_table('Variables', [['${scalar}', 'value'],
                                         ['${slist}', '[s, o, m, e]'],
                                         ['@{list}', 'v1', 'v2', 'v3', 'v4']])
        assert_equals(len(self._datafile.variable_table.variables), 3)
        self._assert_variable(0, '${scalar}', ['value'])
        self._assert_variable(1, '${slist}', ['[s, o, m, e]'])
        self._assert_variable(2, '@{list}', ['v1', 'v2', 'v3', 'v4'])

    def test_line_continuation(self):
        self._create_table('Variables', [['@{list}'],
                                         ['...', 'v1'],
                                         ['', '...', 'v2'],
                                         ['', '', '...', 'v3', 'v4']])
        self._assert_variable(0, '@{list}', ['v1', 'v2', 'v3', 'v4'])

    def test_continuing_in_the_begining_of_the_table(self):
        self._create_table('Variables', [['...', 'val']])
        self._assert_variable(0, '...',  ['val'])



class TestCaseTablePopulatingTest(_PopulatorTest):

    def test_test_case_populating(self):
        self._create_table('Test cases', [['My test name'],
                                          ['', 'No operation'],
                                          ['Another test'],
                                          ['', 'Log', 'quux']])
        assert_equals(len(self._datafile.testcase_table.tests), 2)
        test = self._first_test()
        assert_equals(len(test.steps), 1)
        assert_equals(test.steps[0].name, 'No operation')
        assert_equals(len(self._first_test().steps), 1)

    def test_case_name_and_first_step_on_same_row(self):
        self._create_table('Test cases', [['My test name', 'No Operation']])
        assert_equals(len(self._first_test().steps), 1)

    def test_continuing_in_the_begining_of_the_table(self):
        self._create_table('test cases', [['...', 'foo']])
        assert_equals(self._first_test().name, '...')

    def test_line_continuation(self):
        self._create_table('Test cases', [['My test name', 'Log Many', 'foo'],
                                          ['', '...', 'bar', 'quux'],
                                          ['Another test'],
                                          ['', 'Log Many', 'quux'],
                                          ['', '', '...', 'fooness'],
                                          ['', '', '', '...', 'and more'],
                                          ['', 'Log', 'barness']])
        self._number_of_steps_should_be((self._first_test()), 1)
        self._number_of_steps_should_be(self._nth_test(2), 2)
        assert_equals(self._nth_test(2).steps[0].name, 'Log Many')
        assert_equals(self._nth_test(2).steps[0].args, ['quux', 'fooness', 'and more'])

    def test_unnamed_testcase(self):
        self._create_table('test cases', [['', 'foo', '#comment'],
                                          ['', '[documentation]', "What's up doc?"]])
        test = self._first_test()
        assert_equals(test.name, '')
        assert_equals(test.doc.value, "What's up doc?")
        assert_equals(test.steps[0].comment.as_list(), ['#comment'])

    def test_unnamed_test_and_line_continuation(self):
        self._create_table('test cases', [['', '...', 'foo', '# comment']])
        assert_equals(self._first_test().name, '')
        assert_equals(self._first_test().steps[0].name, 'foo')
        assert_equals(self._first_test().steps[0].comment.as_list(), ['# comment'])

    def test_test_settings(self):
        self._try_test_settings([['My test name'],
                                ['', '[Documentation]', 'This is domumentation for the test case'],
                                ['', '[  Tags  ]', 'ankka', 'kameli'],
                                ['', '... ', '', 'aasi'],
                                ['', 'Log', 'barness']])

    def test_test_settings_with_colons(self):
        self._try_test_settings([['My test name'],
                                ['', '[Documentation:]', 'This is domumentation for the test case'],
                                ['', '[  Tags  :  ]', 'ankka', 'kameli'],
                                ['', '... ', '', 'aasi'],
                                ['', 'Log', 'barness']])

    def _try_test_settings(self, table):
        self._create_table('Test cases', table)
        test = self._first_test()
        assert_equals(len(test.steps), 1)
        assert_equals(test.doc.value, 'This is domumentation for the test case')
        assert_equals(test.tags.value, ['ankka', 'kameli', '', 'aasi'])

    def test_invalid_test_settings(self):
        self._create_table('Test cases', [['My test name'],
                                          ['', '[Aasi]']])
        assert_equals(self._logger.value(), "Error in file 'None': "
                                            "Invalid syntax in test case "
                                            "'My test name': Non-existing "
                                            "setting 'Aasi'.")

    def test_test_template_overrides_setting(self):
        setting_test_template = 'Foo'
        test_test_template = 'Bar'
        self._create_table('Settings', [['Test Template', setting_test_template]],
                           eof=False)
        self._create_table('Test Cases', [['','[Template]', test_test_template]])
        test = self._first_test()
        assert_equals(test.template.value, test_test_template)


class UserKeywordTablePopulatingTest(_PopulatorTest):

    def test_user_keyword_populating(self):
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

    def test_continuing_in_the_begining_of_the_table(self):
        self._create_table('keywords', [['...', 'foo']])
        assert_equals(self._nth_uk(1).name, '...')

    def test_invalid_keyword_settings(self):
        self._create_table('Keywords', [['My User Keyword'],
                                        ['', '[ank ka]']])
        assert_equals(self._logger.value(), "Error in file 'None': "
                                            "Invalid syntax in keyword "
                                            "'My User Keyword': Non-existing "
                                            "setting 'ank ka'.")


class ForLoopPopulatingTest(_PopulatorTest):

    def test_single_loop(self):
        self._create_table('Test cases', [['For loop test'],
                                          ['', ':FOR', '${i}', 'IN', '@{list}'],
                                          ['', '', 'Log', '${i}']])
        assert_equals(len(self._first_test().steps), 1)
        for_loop = self._first_test().steps[0]
        assert_equals(len(for_loop.steps), 1)
        assert_equals(for_loop.flavor, 'IN')
        assert_equals(for_loop.vars, ['${i}'])
        assert_equals(for_loop.items, ['@{list}'])

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
        assert_equals(for_loop.flavor, 'IN RANGE')
        assert_equals(for_loop.vars, ['${i}', '${j}'])

    def test_line_continuation(self):
        self._create_table('Test cases', [['Malicious for loop test'],
                                          ['', 'Log', 'Before FOR'],
                                          ['', '::::   fOr', '${i}', 'IN', '10'],
                                          ['', '...', '20'],
                                          ['', '', '...', '30', '40'],
                                          ['', '', '', '...', '50', '60'],
                                          ['', '', 'Log Many', '${i}'],
                                          ['', '', '...', '${i}'],
                                          ['', '...', '${i}'],
                                          ['', 'Log', 'Outside FOR']])
        assert_equals(len(self._first_test().steps), 3)
        for_loop = self._first_test().steps[1]
        assert_equals(len(for_loop.steps), 1)
        assert_equals(for_loop.flavor, 'IN')
        assert_equals(for_loop.vars, ['${i}'])
        assert_equals(for_loop.items, ['10', '20', '30', '40', '50', '60'])

    def test_with_empty_body(self):
        self._create_table('Test cases', [['For loop test'],
                                          ['', ':FOR ', '${var}', 'IN', 'foo'],
                                          ['', 'Log', 'outside FOR']])
        test = self._first_test()
        assert_equals(len(test.steps), 2)
        assert_equals(test.steps[0].steps, [])



class TestPopulatingComments(_PopulatorTest):

    def test_setting_table(self):
        self._create_table('settings', [['Force Tags', 'Foo', 'Bar', '#comment'],
                                        ['Library', 'Foo', '# Lib comment'],
                                        [' #Resource', 'resource.txt'],
                                        ['Resource', 'resource2.txt'],
                                        ['# comment', 'between rows', 'in many cells'],
                                        ['Default Tags', 'Quux', '# also eol'],
                                        ['Variables', 'varz.py'],
                                        ['# between values'],
                                        ['...', 'arg'],
                                        ['Metadata', 'metaname', 'metavalue'],
                                        ['### last line is commented'],
                                        ])
        self._assert_no_parsing_errors()
        self._assert_setting('force_tags', ['Foo', 'Bar'], ['#comment'])
        self._assert_import(0, 'Foo', [], ['# Lib comment'])
        self._assert_import(1, 'resource2.txt', [], ['#Resource', 'resource.txt'])
        self._assert_setting('default_tags', ['Quux'], ['# comment', 'between rows', 'in many cells', '# also eol'])
        self._assert_import(2, 'varz.py', ['arg'], ['# between values'])
        self._assert_meta(0, 'metaname', 'metavalue', ['### last line is commented'])

    def test_variable_table(self):
        self._create_table('variables', [['# before'],
                                         ['${varname}', 'varvalue', '# has comment'],
                                         ['${name}', '# no value'],
                                         ['# middle', 'A', 'B', 'C'],
                                         ['@{items}', '1', '2', '3'],
                                         ['# s1'],
                                         ['', '# s2', ''],
                                         ['', '', '# s3'],
                                         ['@{X}', '# c1'],
                                         ['', '', '# c2'],
                                         ['...', 'V1', '# c3'],
                                         ['# c4'],
                                         ['...', 'V2', '# c5'],
                                         ['###EOT###']])
        self._assert_no_parsing_errors()
        self._assert_variable(0, '', [], ['# before'])
        self._assert_variable(1, '${varname}', ['varvalue'], ['# has comment'])
        self._assert_variable(2, '${name}', [''], ['# no value'])
        self._assert_variable(3, '', [], ['# middle', 'A', 'B', 'C'])
        self._assert_variable(4, '@{items}', ['1', '2', '3'])
        self._assert_variable(5, '', [], ['# s1'])
        self._assert_variable(6, '', [], ['# s2'])
        self._assert_variable(7, '', [], ['# s3'])
        self._assert_variable(8, '@{X}', ['V1', 'V2'], ['# c1', '# c2', '# c3', '# c4', '# c5'])
        self._assert_variable(9, '', [], ['###EOT###'])

    def test_test_case_table(self):
        self._create_table('test cases', [['# start of table comment'],
                                          ['Test case'],
                                          ['', 'No operation', '# step comment'],
                                          ['', '', '#This step has', 'only comment'],
                                          ['Another test', '#comment in name row'],
                                          ['', 'Log many', 'argh'],
                                          ['#', 'Comment between step def'],
                                          ['', '...', 'urgh'],
                                          ['Test with for loop'],
                                          ['',':FOR', '${i}', 'IN', '1', '# FOR comment'],
                                          ['','...', '2', '3', '##continues', 'here'],
                                          ['#commented out in for loop'],
                                          ['', '#commented out in for loop, again'],
                                          ['','', 'Fooness in the bar', '###end commtne'],
                                          ['','# ', '   Barness  '],
                                          ['', 'Lodi']
                                          ])
        self._assert_comment(self._first_test().steps[0], ['# start of table comment'])
        self._assert_comment(self._first_test().steps[1], ['# step comment'])
        self._assert_comment(self._first_test().steps[2], ['#This step has', 'only comment'])
        self._assert_comment(self._nth_test(2).steps[0], ['#comment in name row'])
        self._assert_comment(self._nth_test(2).steps[1], ['#', 'Comment between step def'])
        assert_equals(self._nth_test(2).steps[1].args, ['argh', 'urgh'])
        self._assert_comment(self._nth_test(3).steps[0], ['# FOR comment', '##continues', 'here'])
        self._assert_comment(self._nth_test(3).steps[0].steps[0], ['#commented out in for loop'])
        self._assert_comment(self._nth_test(3).steps[0].steps[1], ['#commented out in for loop, again'])
        self._assert_comment(self._nth_test(3).steps[0].steps[2], ['###end commtne'])
        self._assert_comment(self._nth_test(3).steps[1], ['#', 'Barness'])
        self._number_of_steps_should_be(self._nth_test(3), 3)

    def _assert_comment(self, step, expected_comment):
        assert_equals(step.comment.as_list(), expected_comment)


class DataRowTest(unittest.TestCase):

    def test_commented_row(self):
        assert_true(DataRow(['#start of table comment']).is_commented())

    def test_escaping_empty_cells(self):
        assert_equals(DataRow(['foo', '\\', '']).all, ['foo', ''])


if __name__ == '__main__':
    unittest.main()
