from io import StringIO
import os
import unittest
import tempfile

from robot.utils import PY3
from robot.utils.asserts import assert_equal

from robot.parsing import get_tokens, get_resource_tokens, Token


T = Token


def assert_tokens(source, expected, get_tokens=get_tokens, data_only=False):
    tokens = list(get_tokens(source, data_only))
    assert_equal(len(tokens), len(expected),
                 'Expected %d tokens:\n%s\n\nGot %d tokens:\n%s'
                 % (len(expected), expected, len(tokens), tokens),
                 values=False)
    for act, exp in zip(tokens, expected):
        assert_equal(act, Token(*exp), formatter=repr)


class TestLexSettings(unittest.TestCase):

    def test_suite_settings(self):
        data = '''\
*** Settings ***
Documentation     Doc    in multiple
...               parts
Metadata          Name           Value
MetaData          Multi part     Value    continues
Suite Setup       Log    Hello, world!
suite teardown    Log    <b>The End.</b>    WARN    html=True
Test Setup        None Shall Pass    ${NONE}
TEST TEARDOWN     No Operation
Test Template     NONE
Test Timeout      1 day
Force Tags        foo    bar
Default Tags      zap
'''
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.DOCUMENTATION, 'Documentation', 2, 0),
            (T.ARGUMENT, 'Doc', 2, 18),
            (T.ARGUMENT, 'in multiple', 2, 25),
            (T.ARGUMENT, 'parts', 3, 18),
            (T.EOS, '', 3, 23),
            (T.METADATA, 'Metadata', 4, 0),
            (T.NAME, 'Name', 4, 18),
            (T.ARGUMENT, 'Value', 4, 33),
            (T.EOS, '', 4, 38),
            (T.METADATA, 'MetaData', 5, 0),
            (T.NAME, 'Multi part', 5, 18),
            (T.ARGUMENT, 'Value', 5, 33),
            (T.ARGUMENT, 'continues', 5, 42),
            (T.EOS, '', 5, 51),
            (T.SUITE_SETUP, 'Suite Setup', 6, 0),
            (T.NAME, 'Log', 6, 18),
            (T.ARGUMENT, 'Hello, world!', 6, 25),
            (T.EOS, '', 6, 38),
            (T.SUITE_TEARDOWN, 'suite teardown', 7, 0),
            (T.NAME, 'Log', 7, 18),
            (T.ARGUMENT, '<b>The End.</b>', 7, 25),
            (T.ARGUMENT, 'WARN', 7, 44),
            (T.ARGUMENT, 'html=True', 7, 52),
            (T.EOS, '', 7, 61),
            (T.TEST_SETUP, 'Test Setup', 8, 0),
            (T.NAME, 'None Shall Pass', 8, 18),
            (T.ARGUMENT, '${NONE}', 8, 37),
            (T.EOS, '', 8, 44),
            (T.TEST_TEARDOWN, 'TEST TEARDOWN', 9, 0),
            (T.NAME, 'No Operation', 9, 18),
            (T.EOS, '', 9, 30),
            (T.TEST_TEMPLATE, 'Test Template', 10, 0),
            (T.NAME, 'NONE', 10, 18),
            (T.EOS, '', 10, 22),
            (T.TEST_TIMEOUT, 'Test Timeout', 11, 0),
            (T.ARGUMENT, '1 day', 11, 18),
            (T.EOS, '', 11, 23),
            (T.FORCE_TAGS, 'Force Tags', 12, 0),
            (T.ARGUMENT, 'foo', 12, 18),
            (T.ARGUMENT, 'bar', 12, 25),
            (T.EOS, '', 12, 28),
            (T.DEFAULT_TAGS, 'Default Tags', 13, 0),
            (T.ARGUMENT, 'zap', 13, 18),
            (T.EOS, '', 13, 21),
        ]
        assert_tokens(data, expected, data_only=True)

    def test_imports(self):
        data = '''\
*** Settings ***
Library           String
LIBRARY           XML    lxml=True
Resource          example.resource
Variables         variables.py
VariAbles         variables.py    arg
Documentation     Valid both in suite and resource files.
'''
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.LIBRARY, 'Library', 2, 0),
            (T.NAME, 'String', 2, 18),
            (T.EOS, '', 2, 24),
            (T.LIBRARY, 'LIBRARY', 3, 0),
            (T.NAME, 'XML', 3, 18),
            (T.ARGUMENT, 'lxml=True', 3, 25),
            (T.EOS, '', 3, 34),
            (T.RESOURCE, 'Resource', 4, 0),
            (T.NAME, 'example.resource', 4, 18),
            (T.EOS, '', 4, 34),
            (T.VARIABLES, 'Variables', 5, 0),
            (T.NAME, 'variables.py', 5, 18),
            (T.EOS, '', 5, 30),
            (T.VARIABLES, 'VariAbles', 6, 0),
            (T.NAME, 'variables.py', 6, 18),
            (T.ARGUMENT, 'arg', 6, 34),
            (T.EOS, '', 6, 37),
            (T.DOCUMENTATION, 'Documentation', 7, 0),
            (T.ARGUMENT, 'Valid both in suite and resource files.', 7, 18),
            (T.EOS, '', 7, 57),
        ]
        assert_tokens(data, expected, get_tokens, data_only=True)
        assert_tokens(data, expected, get_resource_tokens, data_only=True)

    def test_with_name(self):
        data = '''\
*** Settings ***
Library         Easter                       WITH NAME    Christmas
Library         Arguments    arg             WITH NAME    One argument
Library         Arguments    arg1    arg2
...                          arg3    arg4    WITH NAME    Four arguments
'''
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.LIBRARY, 'Library', 2, 0),
            (T.NAME, 'Easter', 2, 16),
            (T.WITH_NAME, 'WITH NAME', 2, 45),
            (T.NAME, 'Christmas', 2, 58),
            (T.EOS, '', 2, 67),
            (T.LIBRARY, 'Library', 3, 0),
            (T.NAME, 'Arguments', 3, 16),
            (T.ARGUMENT, 'arg', 3, 29),
            (T.WITH_NAME, 'WITH NAME', 3, 45),
            (T.NAME, 'One argument', 3, 58),
            (T.EOS, '', 3, 70),
            (T.LIBRARY, 'Library', 4, 0),
            (T.NAME, 'Arguments', 4, 16),
            (T.ARGUMENT, 'arg1', 4, 29),
            (T.ARGUMENT, 'arg2', 4, 37),
            (T.ARGUMENT, 'arg3', 5, 29),
            (T.ARGUMENT, 'arg4', 5, 37),
            (T.WITH_NAME, 'WITH NAME', 5, 45),
            (T.NAME, 'Four arguments', 5, 58),
            (T.EOS, '', 5, 72)
        ]
        assert_tokens(data, expected, get_tokens, data_only=True)
        assert_tokens(data, expected, get_resource_tokens, data_only=True)

    def test_test_settings(self):
        data = '''\
*** Test Cases ***
Name
    [Documentation]    Doc    in multiple
    ...                parts
    [Tags]             first    second
    [Setup]            Log    Hello, world!    level=DEBUG
    [Teardown]         No Operation
    [Template]         Log Many
    [Timeout]          ${TIMEOUT}
'''
        expected = [
            (T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
            (T.EOS, '', 1, 18),
            (T.TESTCASE_NAME, 'Name', 2, 0),
            (T.EOS, '', 2, 4),
            (T.DOCUMENTATION, '[Documentation]', 3, 4),
            (T.ARGUMENT, 'Doc', 3, 23),
            (T.ARGUMENT, 'in multiple', 3, 30),
            (T.ARGUMENT, 'parts', 4, 23),
            (T.EOS, '', 4, 28),
            (T.TAGS, '[Tags]', 5, 4),
            (T.ARGUMENT, 'first', 5, 23),
            (T.ARGUMENT, 'second', 5, 32),
            (T.EOS, '', 5, 38),
            (T.SETUP, '[Setup]', 6, 4),
            (T.NAME, 'Log', 6, 23),
            (T.ARGUMENT, 'Hello, world!', 6, 30),
            (T.ARGUMENT, 'level=DEBUG', 6, 47),
            (T.EOS, '', 6, 58),
            (T.TEARDOWN, '[Teardown]', 7, 4),
            (T.NAME, 'No Operation', 7, 23),
            (T.EOS, '', 7, 35),
            (T.TEMPLATE, '[Template]', 8, 4),
            (T.NAME, 'Log Many', 8, 23),
            (T.EOS, '', 8, 31),
            (T.TIMEOUT, '[Timeout]', 9, 4),
            (T.ARGUMENT, '${TIMEOUT}', 9, 23),
            (T.EOS, '', 9, 33)
        ]
        assert_tokens(data, expected, data_only=True)

    def test_keyword_settings(self):
        data = '''\
*** Keywords ***
Name
    [Arguments]        ${arg1}    ${arg2}=default    @{varargs}    &{kwargs}
    [Documentation]    Doc    in multiple
    ...                parts
    [Tags]             first    second
    [Teardown]         No Operation
    [Timeout]          ${TIMEOUT}
    [Return]           Value
'''
        expected = [
            (T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.KEYWORD_NAME, 'Name', 2, 0),
            (T.EOS, '', 2, 4),
            (T.ARGUMENTS, '[Arguments]', 3, 4),
            (T.ARGUMENT, '${arg1}', 3, 23),
            (T.ARGUMENT, '${arg2}=default', 3, 34),
            (T.ARGUMENT, '@{varargs}', 3, 53),
            (T.ARGUMENT, '&{kwargs}', 3, 67),
            (T.EOS, '', 3, 76),
            (T.DOCUMENTATION, '[Documentation]', 4, 4),
            (T.ARGUMENT, 'Doc', 4, 23),
            (T.ARGUMENT, 'in multiple', 4, 30),
            (T.ARGUMENT, 'parts', 5, 23),
            (T.EOS, '', 5, 28),
            (T.TAGS, '[Tags]', 6, 4),
            (T.ARGUMENT, 'first', 6, 23),
            (T.ARGUMENT, 'second', 6, 32),
            (T.EOS, '', 6, 38),
            (T.TEARDOWN, '[Teardown]', 7, 4),
            (T.NAME, 'No Operation', 7, 23),
            (T.EOS, '', 7, 35),
            (T.TIMEOUT, '[Timeout]', 8, 4),
            (T.ARGUMENT, '${TIMEOUT}', 8, 23),
            (T.EOS, '', 8, 33),
            (T.RETURN, '[Return]', 9, 4),
            (T.ARGUMENT, 'Value', 9, 23),
            (T.EOS, '', 9, 28)
        ]
        assert_tokens(data, expected, get_tokens, data_only=True)
        assert_tokens(data, expected, get_resource_tokens, data_only=True)

    def test_invalid_suite_or_resource_settings(self):
        data = '''\
*** Settings ***
Invalid       Value
Oops, I       dit    it    again
'''
        # Values of invalid settings are ignored with `data_only=True`.
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.ERROR, 'Invalid', 2, 0, "Non-existing setting 'Invalid'."),
            (T.EOS, '', 2, 7),
            (T.ERROR, 'Oops, I', 3, 0, "Non-existing setting 'Oops, I'."),
            (T.EOS, '', 3, 7)
        ]
        assert_tokens(data, expected, get_tokens, data_only=True)
        assert_tokens(data, expected, get_resource_tokens, data_only=True)

    def test_suite_settings_not_allowed_in_resource_file(self):
        data = '''\
*** Settings ***
Metadata          Name           Value
Suite Setup       Log    Hello, world!
suite teardown    Log    <b>The End.</b>    WARN    html=True
Test Setup        None Shall Pass    ${NONE}
TEST TEARDOWN     No Operation
Test Template     NONE
Test Timeout      1 day
Force Tags        foo    bar
Default Tags      zap
Documentation     Valid both in suite and resource files.
'''
        # Values of invalid settings are ignored with `data_only=True`.
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.ERROR, 'Metadata', 2, 0, "Non-existing setting 'Metadata'."),
            (T.EOS, '', 2, 8),
            (T.ERROR, 'Suite Setup', 3, 0, "Non-existing setting 'Suite Setup'."),
            (T.EOS, '', 3, 11),
            (T.ERROR, 'suite teardown', 4, 0, "Non-existing setting 'suite teardown'."),
            (T.EOS, '', 4, 14),
            (T.ERROR, 'Test Setup', 5, 0, "Non-existing setting 'Test Setup'."),
            (T.EOS, '', 5, 10),
            (T.ERROR, 'TEST TEARDOWN', 6, 0, "Non-existing setting 'TEST TEARDOWN'."),
            (T.EOS, '', 6, 13),
            (T.ERROR, 'Test Template', 7, 0, "Non-existing setting 'Test Template'."),
            (T.EOS, '', 7, 13),
            (T.ERROR, 'Test Timeout', 8, 0, "Non-existing setting 'Test Timeout'."),
            (T.EOS, '', 8, 12),
            (T.ERROR, 'Force Tags', 9, 0, "Non-existing setting 'Force Tags'."),
            (T.EOS, '', 9, 10),
            (T.ERROR, 'Default Tags', 10, 0, "Non-existing setting 'Default Tags'."),
            (T.EOS, '', 10, 12),
            (T.DOCUMENTATION, 'Documentation', 11, 0),
            (T.ARGUMENT, 'Valid both in suite and resource files.', 11, 18),
            (T.EOS, '', 11, 57)
        ]
        assert_tokens(data, expected, get_resource_tokens, data_only=True)

    def test_too_many_values_for_single_value_suite_settings(self):
        data = '''\
*** Settings ***
Resource         Too    many   values
Test Timeout     Too    much
Test Template    1    2    3    4    5
'''
        # Values of invalid settings are ignored with `data_only=True`.
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.ERROR, 'Resource', 2, 0, "Setting 'Resource' accepts only one value, got 3."),
            (T.EOS, '', 2, 8),
            (T.ERROR, 'Test Timeout', 3, 0, "Setting 'Test Timeout' accepts only one value, got 2."),
            (T.EOS, '', 3, 12),
            (T.ERROR, 'Test Template', 4, 0, "Setting 'Test Template' accepts only one value, got 5."),
            (T.EOS, '', 4, 13),
        ]
        assert_tokens(data, expected, data_only=True)

    def test_too_many_values_for_single_value_test_settings(self):
        data = '''\
*** Test Cases ***
Name
    [Timeout]     This    is    not    good
    [Template]    This    is    bad
'''
        # Values of invalid settings are ignored with `data_only=True`.
        expected = [
            (T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
            (T.EOS, '', 1, 18),
            (T.TESTCASE_NAME, 'Name', 2, 0),
            (T.EOS, '', 2, 4),
            (T.ERROR, '[Timeout]', 3, 4, "Setting 'Timeout' accepts only one value, got 4."),
            (T.EOS, '', 3, 13),
            (T.ERROR, '[Template]', 4, 4, "Setting 'Template' accepts only one value, got 3."),
            (T.EOS, '', 4, 14)
        ]
        assert_tokens(data, expected, data_only=True)

    def test_too_many_values_for_single_value_keyword_settings(self):
        data = '''\
*** Keywords ***
Name
    [Timeout]     This    is    not    good
'''
        # Values of invalid settings are ignored with `data_only=True`.
        expected = [
            (T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.KEYWORD_NAME, 'Name', 2, 0),
            (T.EOS, '', 2, 4),
            (T.ERROR, '[Timeout]', 3, 4, "Setting 'Timeout' accepts only one value, got 4."),
            (T.EOS, '', 3, 13),
        ]
        assert_tokens(data, expected, data_only=True)

    def test_suite_settings_too_many_times(self):
        data = '''\
*** Settings ***
Documentation     Used
Documentation     Ignored
Suite Setup       Used
Suite Setup       Ignored
Suite Teardown    Used
Suite Teardown    Ignored
Test Setup        Used
Test Setup        Ignored
Test Teardown     Used
Test Teardown     Ignored
Test Template     Used
Test Template     Ignored
Test Timeout      Used
Test Timeout      Ignored
Force Tags        Used
Force Tags        Ignored
Default Tags      Used
Default Tags      Ignored
'''
        # Values of invalid settings are ignored with `data_only=True`.
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.DOCUMENTATION, 'Documentation', 2, 0),
            (T.ARGUMENT, 'Used', 2, 18),
            (T.EOS, '', 2, 22),
            (T.ERROR, 'Documentation', 3, 0, "Setting 'Documentation' allowed only once. Only the first value is used."),
            (T.EOS, '', 3, 13),
            (T.SUITE_SETUP, 'Suite Setup', 4, 0),
            (T.NAME, 'Used', 4, 18),
            (T.EOS, '', 4, 22),
            (T.ERROR, 'Suite Setup', 5, 0, "Setting 'Suite Setup' allowed only once. Only the first value is used."),
            (T.EOS, '', 5, 11),
            (T.SUITE_TEARDOWN, 'Suite Teardown', 6, 0),
            (T.NAME, 'Used', 6, 18),
            (T.EOS, '', 6, 22),
            (T.ERROR, 'Suite Teardown', 7, 0, "Setting 'Suite Teardown' allowed only once. Only the first value is used."),
            (T.EOS, '', 7, 14),
            (T.TEST_SETUP, 'Test Setup', 8, 0),
            (T.NAME, 'Used', 8, 18),
            (T.EOS, '', 8, 22),
            (T.ERROR, 'Test Setup', 9, 0, "Setting 'Test Setup' allowed only once. Only the first value is used."),
            (T.EOS, '', 9, 10),
            (T.TEST_TEARDOWN, 'Test Teardown', 10, 0),
            (T.NAME, 'Used', 10, 18),
            (T.EOS, '', 10, 22),
            (T.ERROR, 'Test Teardown', 11, 0, "Setting 'Test Teardown' allowed only once. Only the first value is used."),
            (T.EOS, '', 11, 13),
            (T.TEST_TEMPLATE, 'Test Template', 12, 0),
            (T.NAME, 'Used', 12, 18),
            (T.EOS, '', 12, 22),
            (T.ERROR, 'Test Template', 13, 0, "Setting 'Test Template' allowed only once. Only the first value is used."),
            (T.EOS, '', 13, 13),
            (T.TEST_TIMEOUT, 'Test Timeout', 14, 0),
            (T.ARGUMENT, 'Used', 14, 18),
            (T.EOS, '', 14, 22),
            (T.ERROR, 'Test Timeout', 15, 0, "Setting 'Test Timeout' allowed only once. Only the first value is used."),
            (T.EOS, '', 15, 12),
            (T.FORCE_TAGS, 'Force Tags', 16, 0),
            (T.ARGUMENT, 'Used', 16, 18),
            (T.EOS, '', 16, 22),
            (T.ERROR, 'Force Tags', 17, 0, "Setting 'Force Tags' allowed only once. Only the first value is used."),
            (T.EOS, '', 17, 10),
            (T.DEFAULT_TAGS, 'Default Tags', 18, 0),
            (T.ARGUMENT, 'Used', 18, 18),
            (T.EOS, '', 18, 22),
            (T.ERROR, 'Default Tags', 19, 0, "Setting 'Default Tags' allowed only once. Only the first value is used."),
            (T.EOS, '', 19, 12)
        ]
        assert_tokens(data, expected, data_only=True)

    def test_test_settings_too_many_times(self):
        data = '''\
*** Test Cases ***
Name
    [Documentation]    Used
    [Documentation]    Ignored
    [Tags]             Used
    [Tags]             Ignored
    [Setup]            Used
    [Setup]            Ignored
    [Teardown]         Used
    [Teardown]         Ignored
    [Template]         Used
    [Template]         Ignored
    [Timeout]          Used
    [Timeout]          Ignored
'''
        # Values of invalid settings are ignored with `data_only=True`.
        expected = [
            (T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
            (T.EOS, '', 1, 18),
            (T.TESTCASE_NAME, 'Name', 2, 0),
            (T.EOS, '', 2, 4),
            (T.DOCUMENTATION, '[Documentation]', 3, 4),
            (T.ARGUMENT, 'Used', 3, 23),
            (T.EOS, '', 3, 27),
            (T.ERROR, '[Documentation]', 4, 4, "Setting 'Documentation' allowed only once. Only the first value is used."),
            (T.EOS, '', 4, 19),
            (T.TAGS, '[Tags]', 5, 4),
            (T.ARGUMENT, 'Used', 5, 23),
            (T.EOS, '', 5, 27),
            (T.ERROR, '[Tags]', 6, 4, "Setting 'Tags' allowed only once. Only the first value is used."),
            (T.EOS, '', 6, 10),
            (T.SETUP, '[Setup]', 7, 4),
            (T.NAME, 'Used', 7, 23),
            (T.EOS, '', 7, 27),
            (T.ERROR, '[Setup]', 8, 4, "Setting 'Setup' allowed only once. Only the first value is used."),
            (T.EOS, '', 8, 11),
            (T.TEARDOWN, '[Teardown]', 9, 4),
            (T.NAME, 'Used', 9, 23),
            (T.EOS, '', 9, 27),
            (T.ERROR, '[Teardown]', 10, 4, "Setting 'Teardown' allowed only once. Only the first value is used."),
            (T.EOS, '', 10, 14),
            (T.TEMPLATE, '[Template]', 11, 4),
            (T.NAME, 'Used', 11, 23),
            (T.EOS, '', 11, 27),
            (T.ERROR, '[Template]', 12, 4, "Setting 'Template' allowed only once. Only the first value is used."),
            (T.EOS, '', 12, 14),
            (T.TIMEOUT, '[Timeout]', 13, 4),
            (T.ARGUMENT, 'Used', 13, 23),
            (T.EOS, '', 13, 27),
            (T.ERROR, '[Timeout]', 14, 4, "Setting 'Timeout' allowed only once. Only the first value is used."),
            (T.EOS, '', 14, 13)
        ]
        assert_tokens(data, expected, data_only=True)

    def test_keyword_settings_too_many_times(self):
        data = '''\
*** Keywords ***
Name
    [Documentation]    Used
    [Documentation]    Ignored
    [Tags]             Used
    [Tags]             Ignored
    [Arguments]        Used
    [Arguments]        Ignored
    [Teardown]         Used
    [Teardown]         Ignored
    [Timeout]          Used
    [Timeout]          Ignored
    [Return]           Used
    [Return]           Ignored
'''
        # Values of invalid settings are ignored with `data_only=True`.
        expected = [
            (T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.KEYWORD_NAME, 'Name', 2, 0),
            (T.EOS, '', 2, 4),
            (T.DOCUMENTATION, '[Documentation]', 3, 4),
            (T.ARGUMENT, 'Used', 3, 23),
            (T.EOS, '', 3, 27),
            (T.ERROR, '[Documentation]', 4, 4, "Setting 'Documentation' allowed only once. Only the first value is used."),
            (T.EOS, '', 4, 19),
            (T.TAGS, '[Tags]', 5, 4),
            (T.ARGUMENT, 'Used', 5, 23),
            (T.EOS, '', 5, 27),
            (T.ERROR, '[Tags]', 6, 4, "Setting 'Tags' allowed only once. Only the first value is used."),
            (T.EOS, '', 6, 10),
            (T.ARGUMENTS, '[Arguments]', 7, 4),
            (T.ARGUMENT, 'Used', 7, 23),
            (T.EOS, '', 7, 27),
            (T.ERROR, '[Arguments]', 8, 4, "Setting 'Arguments' allowed only once. Only the first value is used."),
            (T.EOS, '', 8, 15),
            (T.TEARDOWN, '[Teardown]', 9, 4),
            (T.NAME, 'Used', 9, 23),
            (T.EOS, '', 9, 27),
            (T.ERROR, '[Teardown]', 10, 4, "Setting 'Teardown' allowed only once. Only the first value is used."),
            (T.EOS, '', 10, 14),
            (T.TIMEOUT, '[Timeout]', 11, 4),
            (T.ARGUMENT, 'Used', 11, 23),
            (T.EOS, '', 11, 27),
            (T.ERROR, '[Timeout]', 12, 4, "Setting 'Timeout' allowed only once. Only the first value is used."),
            (T.EOS, '', 12, 13),
            (T.RETURN, '[Return]', 13, 4),
            (T.ARGUMENT, 'Used', 13, 23),
            (T.EOS, '', 13, 27),
            (T.ERROR, '[Return]', 14, 4, "Setting 'Return' allowed only once. Only the first value is used."),
            (T.EOS, '', 14, 12)
        ]
        assert_tokens(data, expected, data_only=True)


class TestName(unittest.TestCase):

    def test_name_on_own_row(self):
        self._verify('My Name',
                     [(T.TESTCASE_NAME, 'My Name', 2, 0), (T.EOL, '', 2, 7), (T.EOS, '', 2, 7)])
        self._verify('My Name    ',
                     [(T.TESTCASE_NAME, 'My Name', 2, 0), (T.EOL, '    ', 2, 7), (T.EOS, '', 2, 11)])
        self._verify('My Name\n    Keyword',
                     [(T.TESTCASE_NAME, 'My Name', 2, 0), (T.EOL, '\n', 2, 7), (T.EOS, '', 2, 8),
                      (T.SEPARATOR, '    ', 3, 0), (T.KEYWORD, 'Keyword', 3, 4), (T.EOL, '', 3, 11), (T.EOS, '', 3, 11)])
        self._verify('My Name  \n    Keyword',
                     [(T.TESTCASE_NAME, 'My Name', 2, 0), (T.EOL, '  \n', 2, 7), (T.EOS, '', 2, 10),
                      (T.SEPARATOR, '    ', 3, 0), (T.KEYWORD, 'Keyword', 3, 4), (T.EOL, '', 3, 11), (T.EOS, '', 3, 11)])

    def test_name_and_keyword_on_same_row(self):
        self._verify('Name    Keyword',
                     [(T.TESTCASE_NAME, 'Name', 2, 0), (T.EOS, '', 2, 4), (T.SEPARATOR, '    ', 2, 4),
                      (T.KEYWORD, 'Keyword', 2, 8), (T.EOL, '', 2, 15), (T.EOS, '', 2, 15)])
        self._verify('N  K  A',
                     [(T.TESTCASE_NAME, 'N', 2, 0), (T.EOS, '', 2, 1), (T.SEPARATOR, '  ', 2, 1),
                      (T.KEYWORD, 'K', 2, 3), (T.SEPARATOR, '  ', 2, 4),
                      (T.ARGUMENT, 'A', 2, 6), (T.EOL, '', 2, 7), (T.EOS, '', 2, 7)])
        self._verify('N  ${v}=  K',
                     [(T.TESTCASE_NAME, 'N', 2, 0), (T.EOS, '', 2, 1), (T.SEPARATOR, '  ', 2, 1),
                      (T.ASSIGN, '${v}=', 2, 3), (T.SEPARATOR, '  ', 2, 8),
                      (T.KEYWORD, 'K', 2, 10), (T.EOL, '', 2, 11), (T.EOS, '', 2, 11)])

    def test_name_and_setting_on_same_row(self):
        self._verify('Name    [Documentation]    The doc.',
                     [(T.TESTCASE_NAME, 'Name', 2, 0), (T.EOS, '', 2, 4), (T.SEPARATOR, '    ', 2, 4),
                      (T.DOCUMENTATION, '[Documentation]', 2, 8), (T.SEPARATOR, '    ', 2, 23),
                      (T.ARGUMENT, 'The doc.', 2, 27), (T.EOL, '', 2, 35), (T.EOS, '', 2, 35)])

    def _verify(self, data, tokens):
        assert_tokens('*** Test Cases ***\n' + data,
                      [(T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
                       (T.EOL, '\n', 1, 18),
                       (T.EOS, '', 1, 19)] + tokens)
        tokens[0] = (T.KEYWORD_NAME,) + tokens[0][1:]
        assert_tokens('*** Keywords ***\n' + data,
                      [(T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
                       (T.EOL, '\n', 1, 16),
                       (T.EOS, '', 1, 17)] + tokens,
                      get_tokens=get_resource_tokens)


class TestNameWithPipes(unittest.TestCase):

    def test_name_on_own_row(self):
        self._verify('| My Name',
                     [(T.SEPARATOR, '| ', 2, 0), (T.TESTCASE_NAME, 'My Name', 2, 2), (T.EOL, '', 2, 9), (T.EOS, '', 2, 9)])
        self._verify('| My Name |',
                     [(T.SEPARATOR, '| ', 2, 0), (T.TESTCASE_NAME, 'My Name', 2, 2), (T.SEPARATOR, ' |', 2, 9), (T.EOL, '', 2, 11), (T.EOS, '', 2, 11)])
        self._verify('| My Name | ',
                     [(T.SEPARATOR, '| ', 2, 0), (T.TESTCASE_NAME, 'My Name', 2, 2), (T.SEPARATOR, ' |', 2, 9), (T.EOL, ' ', 2, 11), (T.EOS, '', 2, 12)])

    def test_name_and_keyword_on_same_row(self):
        self._verify('| Name | Keyword',
                     [(T.SEPARATOR, '| ', 2, 0), (T.TESTCASE_NAME, 'Name', 2, 2), (T.EOS, '', 2, 6),
                      (T.SEPARATOR, ' | ', 2, 6), (T.KEYWORD, 'Keyword', 2, 9), (T.EOL, '', 2, 16), (T.EOS, '', 2, 16)])
        self._verify('| N | K | A |\n',
                     [(T.SEPARATOR, '| ', 2, 0), (T.TESTCASE_NAME, 'N', 2, 2), (T.EOS, '', 2, 3),
                      (T.SEPARATOR, ' | ', 2, 3), (T.KEYWORD, 'K', 2, 6), (T.SEPARATOR, ' | ', 2, 7),
                      (T.ARGUMENT, 'A', 2, 10), (T.SEPARATOR, ' |', 2, 11), (T.EOL, '\n', 2, 13), (T.EOS, '', 2, 14)])
        self._verify('|    N  |  ${v} =    |    K    ',
                     [(T.SEPARATOR, '|    ', 2, 0), (T.TESTCASE_NAME, 'N', 2, 5), (T.EOS, '', 2, 6),
                      (T.SEPARATOR, '  |  ', 2, 6), (T.ASSIGN, '${v} =', 2, 11), (T.SEPARATOR, '    |    ', 2, 17),
                      (T.KEYWORD, 'K', 2, 26), (T.EOL, '    ', 2, 27), (T.EOS, '', 2, 31)])

    def test_name_and_setting_on_same_row(self):
        self._verify('| Name | [Documentation] | The doc.',
                     [(T.SEPARATOR, '| ', 2, 0), (T.TESTCASE_NAME, 'Name', 2, 2), (T.EOS, '', 2, 6), (T.SEPARATOR, ' | ', 2, 6),
                      (T.DOCUMENTATION, '[Documentation]', 2, 9), (T.SEPARATOR, ' | ', 2, 24),
                      (T.ARGUMENT, 'The doc.', 2, 27), (T.EOL, '', 2, 35), (T.EOS, '', 2, 35)])

    def _verify(self, data, tokens):
        assert_tokens('*** Test Cases ***\n' + data,
                      [(T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
                       (T.EOL, '\n', 1, 18),
                       (T.EOS, '', 1, 19)] + tokens)
        tokens[1] = (T.KEYWORD_NAME,) + tokens[1][1:]
        assert_tokens('*** Keywords ***\n' + data,
                      [(T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
                       (T.EOL, '\n', 1, 16),
                       (T.EOS, '', 1, 17)] + tokens,
                      get_tokens=get_resource_tokens)


class TestCommentRowsAndEmptyRows(unittest.TestCase):

    def test_between_names(self):
        self._verify('Name\n#Comment\n\nName 2',
                     [(T.TESTCASE_NAME, 'Name', 2, 0),
                      (T.EOL, '\n', 2, 4),
                      (T.EOS, '', 2, 5),
                      (T.COMMENT, '#Comment', 3, 0),
                      (T.EOL, '\n', 3, 8),
                      (T.EOS, '', 3, 9),
                      (T.EOL, '\n', 4, 0),
                      (T.EOS, '', 4, 1),
                      (T.TESTCASE_NAME, 'Name 2', 5, 0),
                      (T.EOL, '', 5, 6),
                      (T.EOS, '', 5, 6)])

    def test_leading(self):
        self._verify('\n#Comment\n\nName',
                     [(T.EOL, '\n', 2, 0),
                      (T.EOS, '', 2, 1),
                      (T.COMMENT, '#Comment', 3, 0),
                      (T.EOL, '\n', 3, 8),
                      (T.EOS, '', 3, 9),
                      (T.EOL, '\n', 4, 0),
                      (T.EOS, '', 4, 1),
                      (T.TESTCASE_NAME, 'Name', 5, 0),
                      (T.EOL, '', 5, 4),
                      (T.EOS, '', 5, 4)])

    def test_trailing(self):
        self._verify('Name\n#Comment\n\n',
                     [(T.TESTCASE_NAME, 'Name', 2, 0),
                      (T.EOL, '\n', 2, 4),
                      (T.EOS, '', 2, 5),
                      (T.COMMENT, '#Comment', 3, 0),
                      (T.EOL, '\n', 3, 8),
                      (T.EOS, '', 3, 9),
                      (T.EOL, '\n', 4, 0),
                      (T.EOS, '', 4, 1)])
        self._verify('Name\n#Comment\n# C2\n\n',
                     [(T.TESTCASE_NAME, 'Name', 2, 0),
                      (T.EOL, '\n', 2, 4),
                      (T.EOS, '', 2, 5),
                      (T.COMMENT, '#Comment', 3, 0),
                      (T.EOL, '\n', 3, 8),
                      (T.EOS, '', 3, 9),
                      (T.COMMENT, '# C2', 4, 0),
                      (T.EOL, '\n', 4, 4),
                      (T.EOS, '', 4, 5),
                      (T.EOL, '\n', 5, 0),
                      (T.EOS, '', 5, 1)])

    def test_on_their_own(self):
        self._verify('\n',
                     [(T.EOL, '\n', 2, 0),
                      (T.EOS, '', 2, 1)])
        self._verify('# comment',
                     [(T.COMMENT, '# comment', 2, 0),
                      (T.EOL, '', 2, 9),
                      (T.EOS, '', 2, 9)])
        self._verify('\n#\n#',
                     [(T.EOL, '\n', 2, 0),
                      (T.EOS, '', 2, 1),
                      (T.COMMENT, '#', 3, 0),
                      (T.EOL, '\n', 3, 1),
                      (T.EOS, '', 3, 2),
                      (T.COMMENT, '#', 4, 0),
                      (T.EOL, '', 4, 1),
                      (T.EOS, '', 4, 1)])

    def _verify(self, data, tokens):
        assert_tokens('*** Test Cases ***\n' + data,
                      [(T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
                       (T.EOL, '\n', 1, 18),
                       (T.EOS, '', 1, 19)] + tokens)
        tokens = [(T.KEYWORD_NAME,) + t[1:] if t[0] == T.TESTCASE_NAME else t
                  for t in tokens]
        assert_tokens('*** Keywords ***\n' + data,
                      [(T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
                       (T.EOL, '\n', 1, 16),
                       (T.EOS, '', 1, 17)] + tokens,
                      get_tokens=get_resource_tokens)


class TestGetTokensSourceFormats(unittest.TestCase):
    path = os.path.join(os.getenv('TEMPDIR') or tempfile.gettempdir(),
                        'test_lexer.robot')
    data = u'''\
*** Settings ***
Library         Easter

*** Test Cases ***
Example
    None shall pass    ${NONE}
'''
    tokens = [
        (T.SETTING_HEADER, '*** Settings ***', 1, 0),
        (T.EOL, '\n', 1, 16),
        (T.EOS, '', 1, 17),
        (T.LIBRARY, 'Library', 2, 0),
        (T.SEPARATOR, '         ', 2, 7),
        (T.NAME, 'Easter', 2, 16),
        (T.EOL, '\n', 2, 22),
        (T.EOS, '', 2, 23),
        (T.EOL, '\n', 3, 0),
        (T.EOS, '', 3, 1),
        (T.TESTCASE_HEADER, '*** Test Cases ***', 4, 0),
        (T.EOL, '\n', 4, 18),
        (T.EOS, '', 4, 19),
        (T.TESTCASE_NAME, 'Example', 5, 0),
        (T.EOL, '\n', 5, 7),
        (T.EOS, '', 5, 8),
        (T.SEPARATOR, '    ', 6, 0),
        (T.KEYWORD, 'None shall pass', 6, 4),
        (T.SEPARATOR, '    ', 6, 19),
        (T.ARGUMENT, '${NONE}', 6, 23),
        (T.EOL, '\n', 6, 30),
        (T.EOS, '', 6, 31)
    ]
    data_tokens = [
        (T.SETTING_HEADER, '*** Settings ***', 1, 0),
        (T.EOS, '', 1, 16),
        (T.LIBRARY, 'Library', 2, 0),
        (T.NAME, 'Easter', 2, 16),
        (T.EOS, '', 2, 22),
        (T.TESTCASE_HEADER, '*** Test Cases ***', 4, 0),
        (T.EOS, '', 4, 18),
        (T.TESTCASE_NAME, 'Example', 5, 0),
        (T.EOS, '', 5, 7),
        (T.KEYWORD, 'None shall pass', 6, 4),
        (T.ARGUMENT, '${NONE}', 6, 23),
        (T.EOS, '', 6, 30)
    ]

    @classmethod
    def setUpClass(cls):
        with open(cls.path, 'w') as f:
            f.write(cls.data)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.path)

    def test_string_path(self):
        self._verify(self.path)
        self._verify(self.path, data_only=True)

    if PY3:

        def test_pathlib_path(self):
            from pathlib import Path
            self._verify(Path(self.path))
            self._verify(Path(self.path), data_only=True)

    def test_open_file(self):
        with open(self.path) as f:
            self._verify(f)
        with open(self.path) as f:
            self._verify(f, data_only=True)

    def test_string_io(self):
        self._verify(StringIO(self.data))
        self._verify(StringIO(self.data), data_only=True)

    def test_string(self):
        self._verify(self.data)
        self._verify(self.data, data_only=True)

    def _verify(self, source, data_only=False):
        expected = self.data_tokens if data_only else self.tokens
        assert_tokens(source, expected, data_only=data_only)


class TestGetResourceTokensSourceFormats(TestGetTokensSourceFormats):
    data = u'''\
*** Variable ***
${VAR}    Value

*** KEYWORD ***
NOOP    No Operation
'''
    tokens = [
        (T.VARIABLE_HEADER, '*** Variable ***', 1, 0),
        (T.EOL, '\n', 1, 16),
        (T.EOS, '', 1, 17),
        (T.VARIABLE, '${VAR}', 2, 0),
        (T.SEPARATOR, '    ', 2, 6),
        (T.ARGUMENT, 'Value', 2, 10),
        (T.EOL, '\n', 2, 15),
        (T.EOS, '', 2, 16),
        (T.EOL, '\n', 3, 0),
        (T.EOS, '', 3, 1),
        (T.KEYWORD_HEADER, '*** KEYWORD ***', 4, 0),
        (T.EOL, '\n', 4, 15),
        (T.EOS, '', 4, 16),
        (T.KEYWORD_NAME, 'NOOP', 5, 0),
        (T.EOS, '', 5, 4),
        (T.SEPARATOR, '    ', 5, 4),
        (T.KEYWORD, 'No Operation', 5, 8),
        (T.EOL, '\n', 5, 20),
        (T.EOS, '', 5, 21)
    ]
    data_tokens = [
        (T.VARIABLE_HEADER, '*** Variable ***', 1, 0),
        (T.EOS, '', 1, 16),
        (T.VARIABLE, '${VAR}', 2, 0),
        (T.ARGUMENT, 'Value', 2, 10),
        (T.EOS, '', 2, 15),
        (T.KEYWORD_HEADER, '*** KEYWORD ***', 4, 0),
        (T.EOS, '', 4, 15),
        (T.KEYWORD_NAME, 'NOOP', 5, 0),
        (T.EOS, '', 5, 4),
        (T.KEYWORD, 'No Operation', 5, 8),
        (T.EOS, '', 5, 20)
    ]

    def _verify(self, source, data_only=False):
        expected = self.data_tokens if data_only else self.tokens
        assert_tokens(source, expected, get_tokens=get_resource_tokens,
                      data_only=data_only)


if __name__ == '__main__':
    unittest.main()
