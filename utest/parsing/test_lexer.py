import os
import unittest
import tempfile
from io import StringIO
from pathlib import Path

from robot.conf import Language, Languages
from robot.utils.asserts import assert_equal
from robot.parsing import get_tokens, get_init_tokens, get_resource_tokens, Token


T = Token


def assert_tokens(source, expected, get_tokens=get_tokens, **config):
    tokens = list(get_tokens(source, **config))
    assert_equal(len(tokens), len(expected),
                 'Expected %d tokens:\n%s\n\nGot %d tokens:\n%s'
                 % (len(expected), format_tokens(expected),
                    len(tokens), format_tokens(tokens)),
                 values=False)
    for act, exp in zip(tokens, expected):
        assert_equal(act, Token(*exp), formatter=repr)


def format_tokens(tokens):
    return '\n'.join(repr(t) for t in tokens)


class TestLexSettingsSection(unittest.TestCase):

    def test_common_suite_settings(self):
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
Test Timeout      1 day
Test Tags         foo    bar
Keyword Tags      tag
Name              Custom Suite Name
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
            (T.TEST_TIMEOUT, 'Test Timeout', 10, 0),
            (T.ARGUMENT, '1 day', 10, 18),
            (T.EOS, '', 10, 23),
            (T.TEST_TAGS, 'Test Tags', 11, 0),
            (T.ARGUMENT, 'foo', 11, 18),
            (T.ARGUMENT, 'bar', 11, 25),
            (T.EOS, '', 11, 28),
            (T.KEYWORD_TAGS, 'Keyword Tags', 12, 0),
            (T.ARGUMENT, 'tag', 12, 18),
            (T.EOS, '', 12, 21),
            (T.SUITE_NAME, 'Name', 13, 0),
            (T.ARGUMENT, 'Custom Suite Name', 13, 18),
            (T.EOS, '', 13, 35)
        ]
        assert_tokens(data, expected, get_tokens, data_only=True)
        assert_tokens(data, expected, get_init_tokens, data_only=True)

    def test_suite_settings_not_allowed_in_init_file(self):
        data = '''\
*** Settings ***
Test Template     Not allowed in init file
Test Tags         Allowed in both
Default Tags      Not allowed in init file
'''
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.TEST_TEMPLATE, 'Test Template', 2, 0),
            (T.NAME, 'Not allowed in init file', 2, 18),
            (T.EOS, '', 2, 42),
            (T.TEST_TAGS, 'Test Tags', 3, 0),
            (T.ARGUMENT, 'Allowed in both', 3, 18),
            (T.EOS, '', 3, 33),
            (T.DEFAULT_TAGS, 'Default Tags', 4, 0),
            (T.ARGUMENT, 'Not allowed in init file', 4, 18),
            (T.EOS, '', 4, 42)
        ]
        assert_tokens(data, expected, get_tokens, data_only=True)
        # Values of invalid settings are ignored with `data_only=True`.
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.ERROR, 'Test Template', 2, 0,
             "Setting 'Test Template' is not allowed in suite initialization file."),
            (T.EOS, '', 2, 13),
            (T.TEST_TAGS, 'Test Tags', 3, 0),
            (T.ARGUMENT, 'Allowed in both', 3, 18),
            (T.EOS, '', 3, 33),
            (T.ERROR, 'Default Tags', 4, 0,
             "Setting 'Default Tags' is not allowed in suite initialization file."),
            (T.EOS, '', 4, 12)
        ]
        assert_tokens(data, expected, get_init_tokens, data_only=True)

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
Test Tags         foo    bar
Default Tags      zap
Task Tags         quux
Documentation     Valid in all data files.
Name              Bad Resource Name
'''
        # Values of invalid settings are ignored with `data_only=True`.
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.ERROR, 'Metadata', 2, 0,
             "Setting 'Metadata' is not allowed in resource file."),
            (T.EOS, '', 2, 8),
            (T.ERROR, 'Suite Setup', 3, 0,
             "Setting 'Suite Setup' is not allowed in resource file."),
            (T.EOS, '', 3, 11),
            (T.ERROR, 'suite teardown', 4, 0,
             "Setting 'suite teardown' is not allowed in resource file."),
            (T.EOS, '', 4, 14),
            (T.ERROR, 'Test Setup', 5, 0,
             "Setting 'Test Setup' is not allowed in resource file."),
            (T.EOS, '', 5, 10),
            (T.ERROR, 'TEST TEARDOWN', 6, 0,
             "Setting 'TEST TEARDOWN' is not allowed in resource file."),
            (T.EOS, '', 6, 13),
            (T.ERROR, 'Test Template', 7, 0,
             "Setting 'Test Template' is not allowed in resource file."),
            (T.EOS, '', 7, 13),
            (T.ERROR, 'Test Timeout', 8, 0,
             "Setting 'Test Timeout' is not allowed in resource file."),
            (T.EOS, '', 8, 12),
            (T.ERROR, 'Test Tags', 9, 0,
             "Setting 'Test Tags' is not allowed in resource file."),
            (T.EOS, '', 9, 9),
            (T.ERROR, 'Default Tags', 10, 0,
             "Setting 'Default Tags' is not allowed in resource file."),
            (T.EOS, '', 10, 12),
            (T.ERROR, 'Task Tags', 11, 0,
             "Setting 'Task Tags' is not allowed in resource file."),
            (T.EOS, '', 11, 9),
            (T.DOCUMENTATION, 'Documentation', 12, 0),
            (T.ARGUMENT, 'Valid in all data files.', 12, 18),
            (T.EOS, '', 12, 42),
            (T.ERROR, "Name", 13, 0,
             "Setting 'Name' is not allowed in resource file."),
            (T.EOS, '', 13, 4)
        ]
        assert_tokens(data, expected, get_resource_tokens, data_only=True)

    def test_imports(self):
        data = '''\
*** Settings ***
Library           String
LIBRARY           XML    lxml=True
Resource          example.resource
resource
Variables         variables.py
VariAbles         variables.py    arg
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
            (T.RESOURCE, 'resource', 5, 0),
            (T.EOS, '', 5, 8),
            (T.VARIABLES, 'Variables', 6, 0),
            (T.NAME, 'variables.py', 6, 18),
            (T.EOS, '', 6, 30),
            (T.VARIABLES, 'VariAbles', 7, 0),
            (T.NAME, 'variables.py', 7, 18),
            (T.ARGUMENT, 'arg', 7, 34),
            (T.EOS, '', 7, 37),
        ]
        assert_tokens(data, expected, get_tokens, data_only=True)
        assert_tokens(data, expected, get_init_tokens, data_only=True)
        assert_tokens(data, expected, get_resource_tokens, data_only=True)

    def test_aliasing_with_as(self):
        data = '''\
*** Settings ***
Library         Easter                       AS    Christmas
Library         Arguments    arg             AS    One argument
Library         Arguments    arg1    arg2
...                          arg3    arg4    AS    Four arguments
'''
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.LIBRARY, 'Library', 2, 0),
            (T.NAME, 'Easter', 2, 16),
            (T.AS, 'AS', 2, 45),
            (T.NAME, 'Christmas', 2, 51),
            (T.EOS, '', 2, 60),
            (T.LIBRARY, 'Library', 3, 0),
            (T.NAME, 'Arguments', 3, 16),
            (T.ARGUMENT, 'arg', 3, 29),
            (T.AS, 'AS', 3, 45),
            (T.NAME, 'One argument', 3, 51),
            (T.EOS, '', 3, 63),
            (T.LIBRARY, 'Library', 4, 0),
            (T.NAME, 'Arguments', 4, 16),
            (T.ARGUMENT, 'arg1', 4, 29),
            (T.ARGUMENT, 'arg2', 4, 37),
            (T.ARGUMENT, 'arg3', 5, 29),
            (T.ARGUMENT, 'arg4', 5, 37),
            (T.AS, 'AS', 5, 45),
            (T.NAME, 'Four arguments', 5, 51),
            (T.EOS, '', 5, 65)
        ]
        assert_tokens(data, expected, get_tokens, data_only=True)
        assert_tokens(data, expected, get_init_tokens, data_only=True)
        assert_tokens(data, expected, get_resource_tokens, data_only=True)

    def test_invalid_settings(self):
        data = '''\
*** Settings ***
Invalid       Value
Library       Valid
Oops, I       dit    it    again
Libra ry      Smallish typo gives us recommendations!
'''
        # Values of invalid settings are ignored with `data_only=True`.
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.ERROR, 'Invalid', 2, 0, "Non-existing setting 'Invalid'."),
            (T.EOS, '', 2, 7),
            (T.LIBRARY, 'Library', 3, 0),
            (T.NAME, 'Valid', 3, 14),
            (T.EOS, '', 3, 19),
            (T.ERROR, 'Oops, I', 4, 0, "Non-existing setting 'Oops, I'."),
            (T.EOS, '', 4, 7),
            (T.ERROR, 'Libra ry', 5, 0, "Non-existing setting 'Libra ry'. "
                                        "Did you mean:\n    Library"),
            (T.EOS, '', 5, 8)
        ]
        assert_tokens(data, expected, get_tokens, data_only=True)
        assert_tokens(data, expected, get_init_tokens, data_only=True)
        assert_tokens(data, expected, get_resource_tokens, data_only=True)

    def test_too_many_values_for_single_value_settings(self):
        data = '''\
*** Settings ***
Resource         Too    many   values
Test Timeout     Too    much
Test Template    1    2    3    4    5
NaMe             This    is    an    invalid    name
'''
        # Values of invalid settings are ignored with `data_only=True`.
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.ERROR, 'Resource', 2, 0,
             "Setting 'Resource' accepts only one value, got 3."),
            (T.EOS, '', 2, 8),
            (T.ERROR, 'Test Timeout', 3, 0,
             "Setting 'Test Timeout' accepts only one value, got 2."),
            (T.EOS, '', 3, 12),
            (T.ERROR, 'Test Template', 4, 0,
             "Setting 'Test Template' accepts only one value, got 5."),
            (T.EOS, '', 4, 13),
            (T.ERROR, 'NaMe', 5, 0,
             "Setting 'NaMe' accepts only one value, got 5."),
            (T.EOS, '', 5, 4),
        ]
        assert_tokens(data, expected, data_only=True)

    def test_setting_too_many_times(self):
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
Test Tags         Used
Test Tags         Ignored
Default Tags      Used
Default Tags      Ignored
Name              Used
Name              Ignored
'''
        # Values of invalid settings are ignored with `data_only=True`.
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.DOCUMENTATION, 'Documentation', 2, 0),
            (T.ARGUMENT, 'Used', 2, 18),
            (T.EOS, '', 2, 22),
            (T.ERROR, 'Documentation', 3, 0,
             "Setting 'Documentation' is allowed only once. Only the first value is used."),
            (T.EOS, '', 3, 13),
            (T.SUITE_SETUP, 'Suite Setup', 4, 0),
            (T.NAME, 'Used', 4, 18),
            (T.EOS, '', 4, 22),
            (T.ERROR, 'Suite Setup', 5, 0,
             "Setting 'Suite Setup' is allowed only once. Only the first value is used."),
            (T.EOS, '', 5, 11),
            (T.SUITE_TEARDOWN, 'Suite Teardown', 6, 0),
            (T.NAME, 'Used', 6, 18),
            (T.EOS, '', 6, 22),
            (T.ERROR, 'Suite Teardown', 7, 0,
             "Setting 'Suite Teardown' is allowed only once. Only the first value is used."),
            (T.EOS, '', 7, 14),
            (T.TEST_SETUP, 'Test Setup', 8, 0),
            (T.NAME, 'Used', 8, 18),
            (T.EOS, '', 8, 22),
            (T.ERROR, 'Test Setup', 9, 0,
             "Setting 'Test Setup' is allowed only once. Only the first value is used."),
            (T.EOS, '', 9, 10),
            (T.TEST_TEARDOWN, 'Test Teardown', 10, 0),
            (T.NAME, 'Used', 10, 18),
            (T.EOS, '', 10, 22),
            (T.ERROR, 'Test Teardown', 11, 0,
             "Setting 'Test Teardown' is allowed only once. Only the first value is used."),
            (T.EOS, '', 11, 13),
            (T.TEST_TEMPLATE, 'Test Template', 12, 0),
            (T.NAME, 'Used', 12, 18),
            (T.EOS, '', 12, 22),
            (T.ERROR, 'Test Template', 13, 0,
             "Setting 'Test Template' is allowed only once. Only the first value is used."),
            (T.EOS, '', 13, 13),
            (T.TEST_TIMEOUT, 'Test Timeout', 14, 0),
            (T.ARGUMENT, 'Used', 14, 18),
            (T.EOS, '', 14, 22),
            (T.ERROR, 'Test Timeout', 15, 0,
             "Setting 'Test Timeout' is allowed only once. Only the first value is used."),
            (T.EOS, '', 15, 12),
            (T.TEST_TAGS, 'Test Tags', 16, 0),
            (T.ARGUMENT, 'Used', 16, 18),
            (T.EOS, '', 16, 22),
            (T.ERROR, 'Test Tags', 17, 0,
             "Setting 'Test Tags' is allowed only once. Only the first value is used."),
            (T.EOS, '', 17, 9),
            (T.DEFAULT_TAGS, 'Default Tags', 18, 0),
            (T.ARGUMENT, 'Used', 18, 18),
            (T.EOS, '', 18, 22),
            (T.ERROR, 'Default Tags', 19, 0,
             "Setting 'Default Tags' is allowed only once. Only the first value is used."),
            (T.EOS, '', 19, 12),
            ("SUITE NAME", 'Name', 20, 0),
            (T.ARGUMENT, 'Used', 20, 18),
            (T.EOS, '', 20, 22),
            (T.ERROR, 'Name', 21, 0,
             "Setting 'Name' is allowed only once. Only the first value is used."),
            (T.EOS, '', 21, 4)
        ]
        assert_tokens(data, expected, data_only=True)


class TestLexTestAndKeywordSettings(unittest.TestCase):

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
    [Setup]            Log    New in RF 7!
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
            (T.SETUP, '[Setup]', 7, 4),
            (T.NAME, 'Log', 7, 23),
            (T.ARGUMENT, 'New in RF 7!', 7, 30),
            (T.EOS, '', 7, 42),
            (T.TEARDOWN, '[Teardown]', 8, 4),
            (T.NAME, 'No Operation', 8, 23),
            (T.EOS, '', 8, 35),
            (T.TIMEOUT, '[Timeout]', 9, 4),
            (T.ARGUMENT, '${TIMEOUT}', 9, 23),
            (T.EOS, '', 9, 33),
            (T.RETURN, '[Return]', 10, 4,
             "The '[Return]' setting is deprecated. Use the 'RETURN' statement instead."),
            (T.ARGUMENT, 'Value', 10, 23),
            (T.EOS, '', 10, 28)
        ]
        assert_tokens(data, expected, get_tokens, data_only=True)
        assert_tokens(data, expected, get_resource_tokens, data_only=True)

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
            (T.ERROR, '[Timeout]', 3, 4,
             "Setting 'Timeout' accepts only one value, got 4."),
            (T.EOS, '', 3, 13),
            (T.ERROR, '[Template]', 4, 4,
             "Setting 'Template' accepts only one value, got 3."),
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
            (T.ERROR, '[Timeout]', 3, 4,
             "Setting 'Timeout' accepts only one value, got 4."),
            (T.EOS, '', 3, 13),
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
            (T.ERROR, '[Documentation]', 4, 4,
             "Setting 'Documentation' is allowed only once. Only the first value is used."),
            (T.EOS, '', 4, 19),
            (T.TAGS, '[Tags]', 5, 4),
            (T.ARGUMENT, 'Used', 5, 23),
            (T.EOS, '', 5, 27),
            (T.ERROR, '[Tags]', 6, 4,
             "Setting 'Tags' is allowed only once. Only the first value is used."),
            (T.EOS, '', 6, 10),
            (T.SETUP, '[Setup]', 7, 4),
            (T.NAME, 'Used', 7, 23),
            (T.EOS, '', 7, 27),
            (T.ERROR, '[Setup]', 8, 4,
             "Setting 'Setup' is allowed only once. Only the first value is used."),
            (T.EOS, '', 8, 11),
            (T.TEARDOWN, '[Teardown]', 9, 4),
            (T.NAME, 'Used', 9, 23),
            (T.EOS, '', 9, 27),
            (T.ERROR, '[Teardown]', 10, 4,
             "Setting 'Teardown' is allowed only once. Only the first value is used."),
            (T.EOS, '', 10, 14),
            (T.TEMPLATE, '[Template]', 11, 4),
            (T.NAME, 'Used', 11, 23),
            (T.EOS, '', 11, 27),
            (T.ERROR, '[Template]', 12, 4,
             "Setting 'Template' is allowed only once. Only the first value is used."),
            (T.EOS, '', 12, 14),
            (T.TIMEOUT, '[Timeout]', 13, 4),
            (T.ARGUMENT, 'Used', 13, 23),
            (T.EOS, '', 13, 27),
            (T.ERROR, '[Timeout]', 14, 4,
             "Setting 'Timeout' is allowed only once. Only the first value is used."),
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
            (T.ERROR, '[Documentation]', 4, 4,
             "Setting 'Documentation' is allowed only once. Only the first value is used."),
            (T.EOS, '', 4, 19),
            (T.TAGS, '[Tags]', 5, 4),
            (T.ARGUMENT, 'Used', 5, 23),
            (T.EOS, '', 5, 27),
            (T.ERROR, '[Tags]', 6, 4,
             "Setting 'Tags' is allowed only once. Only the first value is used."),
            (T.EOS, '', 6, 10),
            (T.ARGUMENTS, '[Arguments]', 7, 4),
            (T.ARGUMENT, 'Used', 7, 23),
            (T.EOS, '', 7, 27),
            (T.ERROR, '[Arguments]', 8, 4,
             "Setting 'Arguments' is allowed only once. Only the first value is used."),
            (T.EOS, '', 8, 15),
            (T.TEARDOWN, '[Teardown]', 9, 4),
            (T.NAME, 'Used', 9, 23),
            (T.EOS, '', 9, 27),
            (T.ERROR, '[Teardown]', 10, 4,
             "Setting 'Teardown' is allowed only once. Only the first value is used."),
            (T.EOS, '', 10, 14),
            (T.TIMEOUT, '[Timeout]', 11, 4),
            (T.ARGUMENT, 'Used', 11, 23),
            (T.EOS, '', 11, 27),
            (T.ERROR, '[Timeout]', 12, 4,
             "Setting 'Timeout' is allowed only once. Only the first value is used."),
            (T.EOS, '', 12, 13),
            (T.RETURN, '[Return]', 13, 4,
             "The '[Return]' setting is deprecated. Use the 'RETURN' statement instead."),
            (T.ARGUMENT, 'Used', 13, 23),
            (T.EOS, '', 13, 27),
            (T.ERROR, '[Return]', 14, 4,
             "Setting 'Return' is allowed only once. Only the first value is used."),
            (T.EOS, '', 14, 12)
        ]
        assert_tokens(data, expected, data_only=True)


class TestSectionHeaders(unittest.TestCase):

    def test_headers_allowed_everywhere(self):
        data = '''\
*** Settings ***
*** SETTINGS ***
***variables***
*VARIABLES*    ARGS    ARGH
*Keywords     ***    ...
...           ***
*** Keywords ***      # Comment
*** Comments ***
Hello, I'm a comment!
*** COMMENTS ***    1    2
...    3
'''
        expected = [
            (T.SETTING_HEADER, '*** Settings ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.SETTING_HEADER, '*** SETTINGS ***', 2, 0),
            (T.EOS, '', 2, 16),
            (T.VARIABLE_HEADER, '***variables***', 3, 0),
            (T.EOS, '', 3, 15),
            (T.VARIABLE_HEADER, '*VARIABLES*', 4, 0),
            (T.VARIABLE_HEADER, 'ARGS', 4, 15),
            (T.VARIABLE_HEADER, 'ARGH', 4, 23),
            (T.EOS, '', 4, 27),
            (T.KEYWORD_HEADER, '*Keywords', 5, 0),
            (T.KEYWORD_HEADER, '***', 5, 14),
            (T.KEYWORD_HEADER, '...', 5, 21),
            (T.KEYWORD_HEADER, '***', 6, 14),
            (T.EOS, '', 6, 17),
            (T.KEYWORD_HEADER, '*** Keywords ***', 7, 0),
            (T.EOS, '', 7, 16),
            (T.COMMENT_HEADER, '*** Comments ***', 8, 0),
            (T.EOS, '', 8, 16),
            (T.COMMENT_HEADER, '*** COMMENTS ***', 10, 0),
            (T.COMMENT_HEADER, '1', 10, 20),
            (T.COMMENT_HEADER, '2', 10, 25),
            (T.COMMENT_HEADER, '3', 11, 7),
            (T.EOS, '', 11, 8)
        ]
        assert_tokens(data, expected, get_tokens, data_only=True)
        assert_tokens(data, expected, get_init_tokens, data_only=True)
        assert_tokens(data, expected, get_resource_tokens, data_only=True)

    def test_test_case_section(self):
        assert_tokens('*** Test Cases ***', [
            (T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
            (T.EOS, '', 1, 18),
        ], data_only=True)

    def test_case_section_causes_error_in_init_file(self):
        assert_tokens('*** Test Cases ***', [
            (T.INVALID_HEADER, '*** Test Cases ***', 1, 0,
             "'Test Cases' section is not allowed in suite initialization file."),
            (T.EOS, '', 1, 18),
        ], get_init_tokens, data_only=True)

    def test_case_section_causes_fatal_error_in_resource_file(self):
        assert_tokens('*** Test Cases ***', [
            (T.INVALID_HEADER, '*** Test Cases ***', 1, 0,
             "Resource file with 'Test Cases' section is invalid."),
            (T.EOS, '', 1, 18),
        ], get_resource_tokens, data_only=True)

    def test_invalid_section_in_test_case_file(self):
        assert_tokens('*** Invalid ***', [
            (T.INVALID_HEADER, '*** Invalid ***', 1, 0,
             "Unrecognized section header '*** Invalid ***'. Valid sections: "
             "'Settings', 'Variables', 'Test Cases', 'Tasks', 'Keywords' and 'Comments'."),
            (T.EOS, '', 1, 15),
        ], data_only=True)

    def test_invalid_section_in_init_file(self):
        assert_tokens('*** S e t t i n g s ***', [
            (T.INVALID_HEADER, '*** S e t t i n g s ***', 1, 0,
             "Unrecognized section header '*** S e t t i n g s ***'. Valid sections: "
             "'Settings', 'Variables', 'Keywords' and 'Comments'."),
            (T.EOS, '', 1, 23),
        ], get_init_tokens, data_only=True)

    def test_invalid_section_in_resource_file(self):
        assert_tokens('*', [
            (T.INVALID_HEADER, '*', 1, 0,
             "Unrecognized section header '*'. Valid sections: "
             "'Settings', 'Variables', 'Keywords' and 'Comments'."),
            (T.EOS, '', 1, 1),
        ], get_resource_tokens, data_only=True)

    def test_singular_headers_are_deprecated(self):
        data = '''\
*** Setting ***
***variable***
*Keyword
*** Comment ***
'''
        expected = [
            (T.SETTING_HEADER, '*** Setting ***', 1, 0,
             "Singular section headers like '*** Setting ***' are deprecated. "
             "Use plural format like '*** Settings ***' instead."),
            (T.EOL, '\n', 1, 15),
            (T.EOS, '', 1, 16),
            (T.VARIABLE_HEADER, '***variable***', 2, 0,
             "Singular section headers like '***variable***' are deprecated. "
             "Use plural format like '*** Variables ***' instead."),
            (T.EOL, '\n', 2, 14),
            (T.EOS, '', 2, 15),
            (T.KEYWORD_HEADER, '*Keyword', 3, 0,
             "Singular section headers like '*Keyword' are deprecated. "
             "Use plural format like '*** Keywords ***' instead."),
            (T.EOL, '\n', 3, 8),
            (T.EOS, '', 3, 9),
            (T.COMMENT_HEADER, '*** Comment ***', 4, 0,
             "Singular section headers like '*** Comment ***' are deprecated. "
             "Use plural format like '*** Comments ***' instead."),
            (T.EOL, '\n', 4, 15),
            (T.EOS, '', 4, 16)
        ]
        assert_tokens(data, expected, get_tokens)
        assert_tokens(data, expected, get_init_tokens)
        assert_tokens(data, expected, get_resource_tokens)
        assert_tokens('*** Test Case ***', [
            (T.TESTCASE_HEADER, '*** Test Case ***', 1, 0,
             "Singular section headers like '*** Test Case ***' are deprecated. "
             "Use plural format like '*** Test Cases ***' instead."),
            (T.EOL, '', 1, 17),
            (T.EOS, '', 1, 17),
        ])


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

    def test_name_and_keyword_on_same_continued_rows(self):
        self._verify('Name\n...    Keyword',
                     [(T.TESTCASE_NAME, 'Name', 2, 0), (T.EOS, '', 2, 4), (T.EOL, '\n', 2, 4),
                      (T.CONTINUATION, '...', 3, 0), (T.SEPARATOR, '    ', 3, 3),
                      (T.KEYWORD, 'Keyword', 3, 7), (T.EOL, '', 3, 14), (T.EOS, '', 3, 14)])

    def test_name_and_setting_on_same_row(self):
        self._verify('Name    [Documentation]    The doc.',
                     [(T.TESTCASE_NAME, 'Name', 2, 0), (T.EOS, '', 2, 4), (T.SEPARATOR, '    ', 2, 4),
                      (T.DOCUMENTATION, '[Documentation]', 2, 8), (T.SEPARATOR, '    ', 2, 23),
                      (T.ARGUMENT, 'The doc.', 2, 27), (T.EOL, '', 2, 35), (T.EOS, '', 2, 35)])

    def test_name_with_extra(self):
        self._verify('Name\n...\n',
                     [(T.TESTCASE_NAME, 'Name', 2, 0), (T.EOS, '', 2, 4), (T.EOL, '\n', 2, 4),
                      (T.CONTINUATION, '...', 3, 0), (T.KEYWORD, '', 3, 3), (T.EOL, '\n', 3, 3), (T.EOS, '', 3, 4)])

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

    def test_name_and_keyword_on_same_continued_row(self):
        self._verify('| Name | \n| ... | Keyword',
                     [(T.SEPARATOR, '| ', 2, 0), (T.TESTCASE_NAME, 'Name', 2, 2), (T.EOS, '', 2, 6), (T.SEPARATOR, ' |', 2, 6), (T.EOL, ' \n', 2, 8),
                      (T.SEPARATOR, '| ', 3, 0), (T.CONTINUATION, '...', 3, 2), (T.SEPARATOR, ' | ', 3, 5),
                      (T.KEYWORD, 'Keyword', 3, 8), (T.EOL, '', 3, 15), (T.EOS, '', 3, 15)])

    def test_name_and_setting_on_same_row(self):
        self._verify('| Name | [Documentation] | The doc.',
                     [(T.SEPARATOR, '| ', 2, 0), (T.TESTCASE_NAME, 'Name', 2, 2), (T.EOS, '', 2, 6), (T.SEPARATOR, ' | ', 2, 6),
                      (T.DOCUMENTATION, '[Documentation]', 2, 9), (T.SEPARATOR, ' | ', 2, 24),
                      (T.ARGUMENT, 'The doc.', 2, 27), (T.EOL, '', 2, 35), (T.EOS, '', 2, 35)])

    def test_name_with_extra(self):
        self._verify('| Name |  |   |\n| ... |',
                     [(T.SEPARATOR, '| ', 2, 0), (T.TESTCASE_NAME, 'Name', 2, 2), (T.EOS, '', 2, 6),
                      (T.SEPARATOR, ' |  ', 2, 6), (T.SEPARATOR, '|   ', 2, 10), (T.SEPARATOR, '|', 2, 14), (T.EOL, '\n', 2, 15),
                      (T.SEPARATOR, '| ', 3, 0), (T.CONTINUATION, '...', 3, 2), (T.KEYWORD, '', 3, 5), (T.SEPARATOR, ' |', 3, 5),
                      (T.EOL, '', 3, 7), (T.EOS, '', 3, 7)])

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


class TestVariables(unittest.TestCase):

    def test_valid(self):
        data = '''\
*** Variables ***
${SCALAR}    value
${LONG}      First part    ${2} part
...          third part
@{LIST}      first    ${SCALAR}    third
&{DICT}      key=value    &{X}
'''
        expected = [
            (T.VARIABLE_HEADER, '*** Variables ***', 1, 0),
            (T.EOS, '', 1, 17),
            (T.VARIABLE, '${SCALAR}', 2, 0),
            (T.ARGUMENT, 'value', 2, 13),
            (T.EOS, '', 2, 18),
            (T.VARIABLE, '${LONG}', 3, 0),
            (T.ARGUMENT, 'First part', 3, 13),
            (T.ARGUMENT, '${2} part', 3, 27),
            (T.ARGUMENT, 'third part', 4, 13),
            (T.EOS, '', 4, 23),
            (T.VARIABLE, '@{LIST}', 5, 0),
            (T.ARGUMENT, 'first', 5, 13),
            (T.ARGUMENT, '${SCALAR}', 5, 22),
            (T.ARGUMENT, 'third', 5, 35),
            (T.EOS, '', 5, 40),
            (T.VARIABLE, '&{DICT}', 6, 0),
            (T.ARGUMENT, 'key=value', 6, 13),
            (T.ARGUMENT, '&{X}', 6, 26),
            (T.EOS, '', 6, 30)
        ]
        self._verify(data, expected)

    def test_valid_with_assign(self):
        data = '''\
*** Variables ***
${SCALAR} =      value
${LONG}=         First part    ${2} part
...              third part
@{LIST} =        first    ${SCALAR}    third
&{DICT} =        key=value    &{X}
'''
        expected = [
            (T.VARIABLE_HEADER, '*** Variables ***', 1, 0),
            (T.EOS, '', 1, 17),
            (T.VARIABLE, '${SCALAR} =', 2, 0),
            (T.ARGUMENT, 'value', 2, 17),
            (T.EOS, '', 2, 22),
            (T.VARIABLE, '${LONG}=', 3, 0),
            (T.ARGUMENT, 'First part', 3, 17),
            (T.ARGUMENT, '${2} part', 3, 31),
            (T.ARGUMENT, 'third part', 4, 17),
            (T.EOS, '', 4, 27),
            (T.VARIABLE, '@{LIST} =', 5, 0),
            (T.ARGUMENT, 'first', 5, 17),
            (T.ARGUMENT, '${SCALAR}', 5, 26),
            (T.ARGUMENT, 'third', 5, 39),
            (T.EOS, '', 5, 44),
            (T.VARIABLE, '&{DICT} =', 6, 0),
            (T.ARGUMENT, 'key=value', 6, 17),
            (T.ARGUMENT, '&{X}', 6, 30),
            (T.EOS, '', 6, 34)
        ]
        self._verify(data, expected)

    def _verify(self, data, expected):
        assert_tokens(data, expected, get_tokens, data_only=True)
        assert_tokens(data, expected, get_resource_tokens, data_only=True)


class TestForLoop(unittest.TestCase):

    def test_for_loop_header(self):
        header = 'FOR    ${i}    IN    foo    bar'
        expected = [
            (T.FOR, 'FOR', 3, 4),
            (T.VARIABLE, '${i}', 3, 11),
            (T.FOR_SEPARATOR, 'IN', 3, 19),
            (T.ARGUMENT, 'foo', 3, 25),
            (T.ARGUMENT, 'bar', 3, 32),
            (T.EOS, '', 3, 35)
        ]
        self._verify(header, expected)

    def _verify(self, header, expected_header):
        data = '''\
*** %s ***
Name
    %s
        Keyword
    END
'''
        body_and_end = [
            (T.KEYWORD, 'Keyword', 4, 8),
            (T.EOS, '', 4, 15),
            (T.END, 'END', 5, 4),
            (T.EOS, '', 5, 7)
        ]
        expected = [
            (T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
            (T.EOS, '', 1, 18),
            (T.TESTCASE_NAME, 'Name', 2, 0),
            (T.EOS, '', 2, 4)
        ] + expected_header + body_and_end
        assert_tokens(data % ('Test Cases', header), expected, data_only=True)

        expected = [
            (T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
            (T.EOS, '', 1, 16),
            (T.KEYWORD_NAME, 'Name', 2, 0),
            (T.EOS, '', 2, 4)
        ] + expected_header + body_and_end
        assert_tokens(data % ('Keywords', header), expected, data_only=True)
        assert_tokens(data % ('Keywords', header), expected,
                      get_resource_tokens, data_only=True)


class TestIf(unittest.TestCase):

    def test_if_only(self):
        block = '''\
    IF    ${True}
        Log Many    foo    bar
    END
'''
        expected = [
            (T.IF, 'IF', 3, 4),
            (T.ARGUMENT, '${True}', 3, 10),
            (T.EOS, '', 3, 17),
            (T.KEYWORD, 'Log Many', 4, 8),
            (T.ARGUMENT, 'foo', 4, 20),
            (T.ARGUMENT, 'bar', 4, 27),
            (T.EOS, '', 4, 30),
            (T.END, 'END', 5, 4),
            (T.EOS, '', 5, 7)
        ]
        self._verify(block, expected)

    def test_with_else(self):
        block = '''\
    IF    ${False}
        Log    foo
    ELSE
        Log    bar
    END
'''
        expected = [
            (T.IF, 'IF', 3, 4),
            (T.ARGUMENT, '${False}', 3, 10),
            (T.EOS, '', 3, 18),
            (T.KEYWORD, 'Log', 4, 8),
            (T.ARGUMENT, 'foo', 4, 15),
            (T.EOS, '', 4, 18),
            (T.ELSE, 'ELSE', 5, 4),
            (T.EOS, '', 5, 8),
            (T.KEYWORD, 'Log', 6,8),
            (T.ARGUMENT, 'bar', 6, 15),
            (T.EOS, '', 6, 18),
            (T.END, 'END', 7, 4),
            (T.EOS, '', 7, 7)
        ]
        self._verify(block, expected)

    def test_with_else_if_and_else(self):
        block = '''\
    IF    ${False}
        Log    foo
    ELSE IF    ${True}
        Log    bar
    ELSE
        Noop
    END
'''
        expected = [
            (T.IF, 'IF', 3, 4),
            (T.ARGUMENT, '${False}', 3, 10),
            (T.EOS, '', 3, 18),
            (T.KEYWORD, 'Log', 4, 8),
            (T.ARGUMENT, 'foo', 4, 15),
            (T.EOS, '', 4, 18),
            (T.ELSE_IF, 'ELSE IF', 5, 4),
            (T.ARGUMENT, '${True}', 5, 15),
            (T.EOS, '', 5, 22),
            (T.KEYWORD, 'Log', 6, 8),
            (T.ARGUMENT, 'bar', 6, 15),
            (T.EOS, '', 6, 18),
            (T.ELSE, 'ELSE', 7, 4),
            (T.EOS, '', 7, 8),
            (T.KEYWORD, 'Noop', 8, 8),
            (T.EOS, '', 8, 12),
            (T.END, 'END', 9, 4),
            (T.EOS, '', 9, 7)
        ]
        self._verify(block, expected)

    def test_multiline_and_comments(self):
        block = '''\
    IF                 # 3
    ...    ${False}    # 4
        Log            # 5
    ...    foo         # 6
    ELSE IF            # 7
    ...    ${True}     # 8
        Log            # 9
    ...    bar         # 10
    ELSE               # 11
        Log            # 12
    ...    zap         # 13
    END                # 14
        '''
        expected = [
            (T.IF, 'IF', 3, 4),
            (T.ARGUMENT, '${False}', 4, 11),
            (T.EOS, '', 4, 19),
            (T.KEYWORD, 'Log', 5, 8),
            (T.ARGUMENT, 'foo', 6, 11),
            (T.EOS, '', 6, 14),
            (T.ELSE_IF, 'ELSE IF', 7, 4),
            (T.ARGUMENT, '${True}', 8, 11),
            (T.EOS, '', 8, 18),
            (T.KEYWORD, 'Log', 9, 8),
            (T.ARGUMENT, 'bar', 10, 11),
            (T.EOS, '', 10, 14),
            (T.ELSE, 'ELSE', 11, 4),
            (T.EOS, '', 11, 8),
            (T.KEYWORD, 'Log', 12, 8),
            (T.ARGUMENT, 'zap', 13, 11),
            (T.EOS, '', 13, 14),
            (T.END, 'END', 14, 4),
            (T.EOS, '', 14, 7)
        ]
        self._verify(block, expected)

    def _verify(self, block, expected_header):
        data = f'''\
*** Test Cases ***
Name
{block}
'''
        expected_tokens = [
            (T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
            (T.EOS, '', 1, 18),
            (T.TESTCASE_NAME, 'Name', 2, 0),
            (T.EOS, '', 2, 4)
        ] + expected_header
        assert_tokens(data, expected_tokens, data_only=True)


class TestInlineIf(unittest.TestCase):

    def test_if_only(self):
        header = '    IF    ${True}    Log Many   foo    bar'
        expected = [
            (T.SEPARATOR, '    ', 3, 0),
            (T.INLINE_IF, 'IF', 3, 4),
            (T.SEPARATOR, '    ', 3, 6),
            (T.ARGUMENT, '${True}', 3, 10),
            (T.EOS, '', 3, 17),
            (T.SEPARATOR, '    ', 3, 17),
            (T.KEYWORD, 'Log Many', 3, 21),
            (T.SEPARATOR, '   ', 3, 29),
            (T.ARGUMENT, 'foo', 3, 32),
            (T.SEPARATOR, '    ', 3, 35),
            (T.ARGUMENT, 'bar', 3, 39),
            (T.EOL, '\n', 3, 42),
            (T.EOS, '', 3, 43),
            (T.END, '', 3, 43),
            (T.EOS, '', 3, 43)
        ]
        self._verify(header, expected)

    def test_with_else(self):
        #             4     10          22     29     36     43     50
        header = '    IF    ${False}    Log    foo    ELSE   Log    bar'
        expected = [
            (T.SEPARATOR, '    ', 3, 0),
            (T.INLINE_IF, 'IF', 3, 4),
            (T.SEPARATOR, '    ', 3, 6),
            (T.ARGUMENT, '${False}', 3, 10),
            (T.EOS, '', 3, 18),
            (T.SEPARATOR, '    ', 3, 18),
            (T.KEYWORD, 'Log', 3, 22),
            (T.SEPARATOR, '    ', 3, 25),
            (T.ARGUMENT, 'foo', 3, 29),
            (T.SEPARATOR, '    ', 3, 32),
            (T.EOS, '', 3, 36),
            (T.ELSE, 'ELSE', 3, 36),
            (T.EOS, '', 3, 40),
            (T.SEPARATOR, '   ', 3, 40),
            (T.KEYWORD, 'Log', 3, 43),
            (T.SEPARATOR, '    ', 3, 46),
            (T.ARGUMENT, 'bar', 3, 50),
            (T.EOL, '\n', 3, 53),
            (T.EOS, '', 3, 54),
            (T.END, '', 3, 54),
            (T.EOS, '', 3, 54)
        ]
        self._verify(header, expected)

    def test_with_else_if_and_else(self):
        #             4     10          22     29     36         47       56     63     70      78
        header = '    IF    ${False}    Log    foo    ELSE IF    ${True}  Log    bar    ELSE    Noop'
        expected = [
            (T.SEPARATOR, '    ', 3, 0),
            (T.INLINE_IF, 'IF', 3, 4),
            (T.SEPARATOR, '    ', 3, 6),
            (T.ARGUMENT, '${False}', 3, 10),
            (T.EOS, '', 3, 18),
            (T.SEPARATOR, '    ', 3, 18),
            (T.KEYWORD, 'Log', 3, 22),
            (T.SEPARATOR, '    ', 3, 25),
            (T.ARGUMENT, 'foo', 3, 29),
            (T.SEPARATOR, '    ', 3, 32),
            (T.EOS, '', 3, 36),
            (T.ELSE_IF, 'ELSE IF', 3, 36),
            (T.SEPARATOR, '    ', 3, 43),
            (T.ARGUMENT, '${True}', 3, 47),
            (T.EOS, '', 3, 54),
            (T.SEPARATOR, '  ', 3, 54),
            (T.KEYWORD, 'Log', 3, 56),
            (T.SEPARATOR, '    ', 3, 59),
            (T.ARGUMENT, 'bar', 3, 63),
            (T.SEPARATOR, '    ', 3, 66),
            (T.EOS, '', 3, 70),
            (T.ELSE, 'ELSE', 3, 70),
            (T.EOS, '', 3, 74),
            (T.SEPARATOR, '    ', 3, 74),
            (T.KEYWORD, 'Noop', 3, 78),
            (T.EOL, '\n', 3, 82),
            (T.EOS, '', 3, 83),
            (T.END, '', 3, 83),
            (T.EOS, '', 3, 83)
        ]
        self._verify(header, expected)

    def test_else_if_with_non_ascii_space(self):
        #             4     10   15    21
        header = '    IF    1    K1    ELSE\N{NO-BREAK SPACE}IF    2    K2'
        expected = [
            (T.SEPARATOR, '    ', 3, 0),
            (T.INLINE_IF, 'IF', 3, 4),
            (T.SEPARATOR, '    ', 3, 6),
            (T.ARGUMENT, '1', 3, 10),
            (T.EOS, '', 3, 11),
            (T.SEPARATOR, '    ', 3, 11),
            (T.KEYWORD, 'K1', 3, 15),
            (T.SEPARATOR, '    ', 3, 17),
            (T.EOS, '', 3, 21),
            (T.ELSE_IF, 'ELSE\N{NO-BREAK SPACE}IF', 3, 21),
            (T.SEPARATOR, '    ', 3, 28),
            (T.ARGUMENT, '2', 3, 32),
            (T.EOS, '', 3, 33),
            (T.SEPARATOR, '    ', 3, 33),
            (T.KEYWORD, 'K2', 3, 37),
            (T.EOL, '\n', 3, 39),
            (T.EOS, '', 3, 40),
            (T.END, '', 3, 40),
            (T.EOS, '', 3, 40)
        ]
        self._verify(header, expected)

    def test_empty_else(self):
        header = '    IF    e    K    ELSE'
        expected = [
            (T.SEPARATOR, '    ', 3, 0),
            (T.INLINE_IF, 'IF', 3, 4),
            (T.SEPARATOR, '    ', 3, 6),
            (T.ARGUMENT, 'e', 3, 10),
            (T.EOS, '', 3, 11),
            (T.SEPARATOR, '    ', 3, 11),
            (T.KEYWORD, 'K', 3, 15),
            (T.SEPARATOR, '    ', 3, 16),
            (T.EOS, '', 3, 20),
            (T.ELSE, 'ELSE', 3, 20),
            (T.EOL, '\n', 3, 24),
            (T.EOS, '', 3, 25),
            (T.END, '', 3, 25),
            (T.EOS, '', 3, 25)
        ]
        self._verify(header, expected)

    def test_empty_else_if(self):
        header = '    IF    e    K    ELSE IF'
        expected = [
            (T.SEPARATOR, '    ', 3, 0),
            (T.INLINE_IF, 'IF', 3, 4),
            (T.SEPARATOR, '    ', 3, 6),
            (T.ARGUMENT, 'e', 3, 10),
            (T.EOS, '', 3, 11),
            (T.SEPARATOR, '    ', 3, 11),
            (T.KEYWORD, 'K', 3, 15),
            (T.SEPARATOR, '    ', 3, 16),
            (T.EOS, '', 3, 20),
            (T.ELSE_IF, 'ELSE IF', 3, 20),
            (T.EOL, '\n', 3, 27),
            (T.EOS, '', 3, 28),
            (T.END, '', 3, 28),
            (T.EOS, '', 3, 28)
        ]
        self._verify(header, expected)

    def test_else_if_with_only_expression(self):
        header = '    IF    e    K    ELSE IF    e'
        expected = [
            (T.SEPARATOR, '    ', 3, 0),
            (T.INLINE_IF, 'IF', 3, 4),
            (T.SEPARATOR, '    ', 3, 6),
            (T.ARGUMENT, 'e', 3, 10),
            (T.EOS, '', 3, 11),
            (T.SEPARATOR, '    ', 3, 11),
            (T.KEYWORD, 'K', 3, 15),
            (T.SEPARATOR, '    ', 3, 16),
            (T.EOS, '', 3, 20),
            (T.ELSE_IF, 'ELSE IF', 3, 20),
            (T.SEPARATOR, '    ', 3, 27),
            (T.ARGUMENT, 'e', 3, 31),
            (T.EOL, '\n', 3, 32),
            (T.EOS, '', 3, 33),
            (T.END, '', 3, 33),
            (T.EOS, '', 3, 33)
        ]
        self._verify(header, expected)

    def test_assign(self):
        #             4         14    20      28    34      42
        header = '    ${x} =    IF    True    K1    ELSE    K2'
        expected = [
            (T.SEPARATOR, '    ', 3, 0),
            (T.ASSIGN, '${x} =', 3, 4),
            (T.SEPARATOR, '    ', 3, 10),
            (T.INLINE_IF, 'IF', 3, 14),
            (T.SEPARATOR, '    ', 3, 16),
            (T.ARGUMENT, 'True', 3, 20),
            (T.EOS, '', 3, 24),
            (T.SEPARATOR, '    ', 3, 24),
            (T.KEYWORD, 'K1', 3, 28),
            (T.SEPARATOR, '    ', 3, 30),
            (T.EOS, '', 3, 34),
            (T.ELSE, 'ELSE', 3, 34),
            (T.EOS, '', 3, 38),
            (T.SEPARATOR, '    ', 3, 38),
            (T.KEYWORD, 'K2', 3, 42),
            (T.EOL, '\n', 3, 44),
            (T.EOS, '', 3, 45),
            (T.END, '', 3, 45),
            (T.EOS, '', 3, 45),
        ]
        self._verify(header, expected)

    def test_assign_with_empty_else(self):
        #             4         14    20      28    34
        header = '    ${x} =    IF    True    K1    ELSE'
        expected = [
            (T.SEPARATOR, '    ', 3, 0),
            (T.ASSIGN, '${x} =', 3, 4),
            (T.SEPARATOR, '    ', 3, 10),
            (T.INLINE_IF, 'IF', 3, 14),
            (T.SEPARATOR, '    ', 3, 16),
            (T.ARGUMENT, 'True', 3, 20),
            (T.EOS, '', 3, 24),
            (T.SEPARATOR, '    ', 3, 24),
            (T.KEYWORD, 'K1', 3, 28),
            (T.SEPARATOR, '    ', 3, 30),
            (T.EOS, '', 3, 34),
            (T.ELSE, 'ELSE', 3, 34),
            (T.EOL, '\n', 3, 38),
            (T.EOS, '', 3, 39),
            (T.END, '', 3, 39),
            (T.EOS, '', 3, 39),
        ]
        self._verify(header, expected)

    def test_multiline_and_comments(self):
        header = '''\
    IF                 # 3
    ...    ${False}    # 4
    ...    Log         # 5
    ...    foo         # 6
    ...    ELSE IF     # 7
    ...    ${True}     # 8
    ...    Log         # 9
    ...    bar         # 10
    ...    ELSE        # 11
    ...    Log         # 12
    ...    zap         # 13
'''
        expected = [
            (T.SEPARATOR, '    ', 3, 0),
            (T.INLINE_IF, 'IF', 3, 4),
            (T.SEPARATOR, '                 ', 3, 6),
            (T.COMMENT, '# 3', 3, 23),
            (T.EOL, '\n', 3, 26),
            (T.SEPARATOR, '    ', 4, 0),
            (T.CONTINUATION, '...', 4, 4),
            (T.SEPARATOR, '    ', 4, 7),
            (T.ARGUMENT, '${False}', 4, 11),
            (T.EOS, '', 4, 19),

            (T.SEPARATOR, '    ', 4, 19),
            (T.COMMENT, '# 4', 4, 23),
            (T.EOL, '\n', 4, 26),
            (T.SEPARATOR, '    ', 5, 0),
            (T.CONTINUATION, '...', 5, 4),
            (T.SEPARATOR, '    ', 5, 7),
            (T.KEYWORD, 'Log', 5, 11),
            (T.SEPARATOR, '         ', 5, 14),
            (T.COMMENT, '# 5', 5, 23),
            (T.EOL, '\n', 5, 26),
            (T.SEPARATOR, '    ', 6, 0),
            (T.CONTINUATION, '...', 6, 4),
            (T.SEPARATOR, '    ', 6, 7),
            (T.ARGUMENT, 'foo', 6, 11),
            (T.SEPARATOR, '         ', 6, 14),
            (T.COMMENT, '# 6', 6, 23),
            (T.EOL, '\n', 6, 26),
            (T.SEPARATOR, '    ', 7, 0),
            (T.CONTINUATION, '...', 7, 4),
            (T.SEPARATOR, '    ', 7, 7),
            (T.EOS, '', 7, 11),

            (T.ELSE_IF, 'ELSE IF', 7, 11),
            (T.SEPARATOR, '     ', 7, 18),
            (T.COMMENT, '# 7', 7, 23),
            (T.EOL, '\n', 7, 26),
            (T.SEPARATOR, '    ', 8, 0),
            (T.CONTINUATION, '...', 8, 4),
            (T.SEPARATOR, '    ', 8, 7),
            (T.ARGUMENT, '${True}', 8, 11),
            (T.EOS, '', 8, 18),

            (T.SEPARATOR, '     ', 8, 18),
            (T.COMMENT, '# 8', 8, 23),
            (T.EOL, '\n', 8, 26),
            (T.SEPARATOR, '    ', 9, 0),
            (T.CONTINUATION, '...', 9, 4),
            (T.SEPARATOR, '    ', 9, 7),
            (T.KEYWORD, 'Log', 9, 11),
            (T.SEPARATOR, '         ', 9, 14),
            (T.COMMENT, '# 9', 9, 23),
            (T.EOL, '\n', 9, 26),
            (T.SEPARATOR, '    ', 10, 0),
            (T.CONTINUATION, '...', 10, 4),
            (T.SEPARATOR, '    ', 10, 7),
            (T.ARGUMENT, 'bar', 10, 11),
            (T.SEPARATOR, '         ', 10, 14),
            (T.COMMENT, '# 10', 10, 23),
            (T.EOL, '\n', 10, 27),
            (T.SEPARATOR, '    ', 11, 0),
            (T.CONTINUATION, '...', 11, 4),
            (T.SEPARATOR, '    ', 11, 7),
            (T.EOS, '', 11, 11),

            (T.ELSE, 'ELSE', 11, 11),
            (T.EOS, '', 11, 15),

            (T.SEPARATOR, '        ', 11, 15),
            (T.COMMENT, '# 11', 11, 23),
            (T.EOL, '\n', 11, 27),
            (T.SEPARATOR, '    ', 12, 0),
            (T.CONTINUATION, '...', 12, 4),
            (T.SEPARATOR, '    ', 12, 7),
            (T.KEYWORD, 'Log', 12, 11),
            (T.SEPARATOR, '         ', 12, 14),
            (T.COMMENT, '# 12', 12, 23),
            (T.EOL, '\n', 12, 27),
            (T.SEPARATOR, '    ', 13, 0),
            (T.CONTINUATION, '...', 13, 4),
            (T.SEPARATOR, '    ', 13, 7),
            (T.ARGUMENT, 'zap', 13, 11),
            (T.SEPARATOR, '         ', 13, 14),
            (T.COMMENT, '# 13', 13, 23),
            (T.EOL, '\n', 13, 27),
            (T.EOS, '', 13, 28),

            (T.END, '', 13, 28),
            (T.EOS, '', 13, 28),
            (T.EOL, '\n', 14, 0),
            (T.EOS, '', 14, 1)
        ]
        self._verify(header, expected)

    def _verify(self, header, expected_header):
        data = f'''\
*** Test Cases ***
Name
{header}
'''
        expected_tokens = [
            (T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
            (T.EOL, '\n', 1, 18),
            (T.EOS, '', 1, 19),
            (T.TESTCASE_NAME, 'Name', 2, 0),
            (T.EOL, '\n', 2, 4),
            (T.EOS, '', 2, 5),
        ] + expected_header
        assert_tokens(data, expected_tokens)


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
    data = '''\
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

    def test_pathlib_path(self):
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
    data = '''\
*** Variables ***
${VAR}    Value

*** KEYWORDS ***
NOOP    No Operation
'''
    tokens = [
        (T.VARIABLE_HEADER, '*** Variables ***', 1, 0),
        (T.EOL, '\n', 1, 17),
        (T.EOS, '', 1, 18),
        (T.VARIABLE, '${VAR}', 2, 0),
        (T.SEPARATOR, '    ', 2, 6),
        (T.ARGUMENT, 'Value', 2, 10),
        (T.EOL, '\n', 2, 15),
        (T.EOS, '', 2, 16),
        (T.EOL, '\n', 3, 0),
        (T.EOS, '', 3, 1),
        (T.KEYWORD_HEADER, '*** KEYWORDS ***', 4, 0),
        (T.EOL, '\n', 4, 16),
        (T.EOS, '', 4, 17),
        (T.KEYWORD_NAME, 'NOOP', 5, 0),
        (T.EOS, '', 5, 4),
        (T.SEPARATOR, '    ', 5, 4),
        (T.KEYWORD, 'No Operation', 5, 8),
        (T.EOL, '\n', 5, 20),
        (T.EOS, '', 5, 21)
    ]
    data_tokens = [
        (T.VARIABLE_HEADER, '*** Variables ***', 1, 0),
        (T.EOS, '', 1, 17),
        (T.VARIABLE, '${VAR}', 2, 0),
        (T.ARGUMENT, 'Value', 2, 10),
        (T.EOS, '', 2, 15),
        (T.KEYWORD_HEADER, '*** KEYWORDS ***', 4, 0),
        (T.EOS, '', 4, 16),
        (T.KEYWORD_NAME, 'NOOP', 5, 0),
        (T.EOS, '', 5, 4),
        (T.KEYWORD, 'No Operation', 5, 8),
        (T.EOS, '', 5, 20)
    ]

    def _verify(self, source, data_only=False):
        expected = self.data_tokens if data_only else self.tokens
        assert_tokens(source, expected, get_tokens=get_resource_tokens,
                      data_only=data_only)


class TestTokenizeVariables(unittest.TestCase):

    def test_settings(self):
        data = '''\
*** Settings ***
Library       My${Name}    my ${arg}    ${x}[0]    AS    Your${Name}
${invalid}    ${usage}
'''
        expected = [(T.SETTING_HEADER, '*** Settings ***', 1, 0),
                    (T.EOS, '', 1, 16),
                    (T.LIBRARY, 'Library', 2, 0),
                    (T.NAME, 'My', 2, 14),
                    (T.VARIABLE, '${Name}', 2, 16),
                    (T.ARGUMENT, 'my ', 2, 27),
                    (T.VARIABLE, '${arg}', 2, 30),
                    (T.VARIABLE, '${x}[0]', 2, 40),
                    (T.AS, 'AS', 2, 51),
                    (T.NAME, 'Your', 2, 57),
                    (T.VARIABLE, '${Name}', 2, 61),
                    (T.EOS, '', 2, 68),
                    (T.ERROR, '${invalid}', 3, 0, "Non-existing setting '${invalid}'."),
                    (T.EOS, '', 3, 10)]
        assert_tokens(data, expected, get_tokens=get_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_resource_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_init_tokens,
                      data_only=True, tokenize_variables=True)

    def test_variables(self):
        data = '''\
*** Variables ***
${VARIABLE}      my ${value}
&{DICT}          key=${var}[item][1:]    ${key}=${a}${b}[c]${d}
'''
        expected = [(T.VARIABLE_HEADER, '*** Variables ***', 1, 0),
                    (T.EOS, '', 1, 17),
                    (T.VARIABLE, '${VARIABLE}', 2, 0),
                    (T.ARGUMENT, 'my ', 2, 17),
                    (T.VARIABLE, '${value}', 2, 20),
                    (T.EOS, '', 2, 28),
                    (T.VARIABLE, '&{DICT}', 3, 0),
                    (T.ARGUMENT, 'key=', 3, 17),
                    (T.VARIABLE, '${var}[item][1:]', 3, 21),
                    (T.VARIABLE, '${key}', 3, 41),
                    (T.ARGUMENT, '=', 3, 47),
                    (T.VARIABLE, '${a}', 3, 48),
                    (T.VARIABLE, '${b}[c]', 3, 52),
                    (T.VARIABLE, '${d}', 3, 59),
                    (T.EOS, '', 3, 63)]
        assert_tokens(data, expected, get_tokens=get_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_resource_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_init_tokens,
                      data_only=True, tokenize_variables=True)

    def test_test_cases(self):
        data = '''\
*** Test Cases ***
My ${name}
    [Documentation]    a ${b} ${c}[d] ${e${f}}
    ${assign} =    Keyword    my ${arg}ument
    Key${word}
${name}
'''
        expected = [(T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
                    (T.EOS, '', 1, 18),
                    (T.TESTCASE_NAME, 'My ', 2, 0),
                    (T.VARIABLE, '${name}', 2, 3),
                    (T.EOS, '', 2, 10),
                    (T.DOCUMENTATION, '[Documentation]', 3, 4),
                    (T.ARGUMENT, 'a ', 3, 23),
                    (T.VARIABLE, '${b}', 3, 25),
                    (T.ARGUMENT, ' ', 3, 29),
                    (T.VARIABLE, '${c}[d]', 3, 30),
                    (T.ARGUMENT, ' ', 3, 37),
                    (T.VARIABLE, '${e${f}}', 3, 38),
                    (T.EOS, '', 3, 46),
                    (T.ASSIGN, '${assign} =', 4, 4),
                    (T.KEYWORD, 'Keyword', 4, 19),
                    (T.ARGUMENT, 'my ', 4, 30),
                    (T.VARIABLE, '${arg}', 4, 33),
                    (T.ARGUMENT, 'ument', 4, 39),
                    (T.EOS, '', 4, 44),
                    (T.KEYWORD, 'Key${word}', 5, 4),
                    (T.EOS, '', 5, 14),
                    (T.VARIABLE, '${name}', 6, 0),
                    (T.EOS, '', 6, 7)]
        assert_tokens(data, expected, get_tokens=get_tokens,
                      data_only=True, tokenize_variables=True)

    def test_keywords(self):
        data = '''\
*** Keywords ***
My ${name}
    [Documentation]    a ${b} ${c}[d] ${e${f}}
    ${assign} =    Keyword    my ${arg}ument
    Key${word}
${name}
'''
        expected = [(T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
                    (T.EOS, '', 1, 16),
                    (T.KEYWORD_NAME, 'My ', 2, 0),
                    (T.VARIABLE, '${name}', 2, 3),
                    (T.EOS, '', 2, 10),
                    (T.DOCUMENTATION, '[Documentation]', 3, 4),
                    (T.ARGUMENT, 'a ', 3, 23),
                    (T.VARIABLE, '${b}', 3, 25),
                    (T.ARGUMENT, ' ', 3, 29),
                    (T.VARIABLE, '${c}[d]', 3, 30),
                    (T.ARGUMENT, ' ', 3, 37),
                    (T.VARIABLE, '${e${f}}', 3, 38),
                    (T.EOS, '', 3, 46),
                    (T.ASSIGN, '${assign} =', 4, 4),
                    (T.KEYWORD, 'Keyword', 4, 19),
                    (T.ARGUMENT, 'my ', 4, 30),
                    (T.VARIABLE, '${arg}', 4, 33),
                    (T.ARGUMENT, 'ument', 4, 39),
                    (T.EOS, '', 4, 44),
                    (T.KEYWORD, 'Key${word}', 5, 4),
                    (T.EOS, '', 5, 14),
                    (T.VARIABLE, '${name}', 6, 0),
                    (T.EOS, '', 6, 7)]
        assert_tokens(data, expected, get_tokens=get_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_resource_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_init_tokens,
                      data_only=True, tokenize_variables=True)


class TestKeywordCallAssign(unittest.TestCase):

    def test_valid_assign(self):
        data = '''\
*** Keywords ***
do something
    ${a}
'''
        expected = [(T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
                    (T.EOS, '', 1, 16),
                    (T.KEYWORD_NAME, 'do something', 2, 0),
                    (T.EOS, '', 2, 12),
                    (T.ASSIGN, '${a}', 3, 4),
                    (T.EOS, '', 3, 8)]

        assert_tokens(data, expected, get_tokens=get_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_resource_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_init_tokens,
                      data_only=True, tokenize_variables=True)

    def test_valid_assign_with_keyword(self):
        data = '''\
*** Keywords ***
do something
    ${a}  do nothing
'''
        expected = [(T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
                    (T.EOS, '', 1, 16),
                    (T.KEYWORD_NAME, 'do something', 2, 0),
                    (T.EOS, '', 2, 12),
                    (T.ASSIGN, '${a}', 3, 4),
                    (T.KEYWORD, 'do nothing', 3, 10),
                    (T.EOS, '', 3, 20)]

        assert_tokens(data, expected, get_tokens=get_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_resource_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_init_tokens,
                      data_only=True, tokenize_variables=True)

    def test_invalid_assign_not_closed_should_be_keyword(self):
        data = '''\
*** Keywords ***
do something
    ${a
'''
        expected = [(T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
                    (T.EOS, '', 1, 16),
                    (T.KEYWORD_NAME, 'do something', 2, 0),
                    (T.EOS, '', 2, 12),
                    (T.KEYWORD, '${a', 3, 4),
                    (T.EOS, '', 3, 7)]

        assert_tokens(data, expected, get_tokens=get_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_resource_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_init_tokens,
                      data_only=True, tokenize_variables=True)

    def test_invalid_assign_ends_with_equal_should_be_keyword(self):
        data = '''\
*** Keywords ***
do something
    ${=
'''
        expected = [(T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
                    (T.EOS, '', 1, 16),
                    (T.KEYWORD_NAME, 'do something', 2, 0),
                    (T.EOS, '', 2, 12),
                    (T.KEYWORD, '${=', 3, 4),
                    (T.EOS, '', 3, 7)]

        assert_tokens(data, expected, get_tokens=get_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_resource_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_init_tokens,
                      data_only=True, tokenize_variables=True)

    def test_invalid_assign_variable_and_ends_with_equal_should_be_keyword(self):
        data = '''\
*** Keywords ***
do something
    ${abc def=
'''
        expected = [(T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
                    (T.EOS, '', 1, 16),
                    (T.KEYWORD_NAME, 'do something', 2, 0),
                    (T.EOS, '', 2, 12),
                    (T.KEYWORD, '${abc def=', 3, 4),
                    (T.EOS, '', 3, 14)]

        assert_tokens(data, expected, get_tokens=get_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_resource_tokens,
                      data_only=True, tokenize_variables=True)
        assert_tokens(data, expected, get_tokens=get_init_tokens,
                      data_only=True, tokenize_variables=True)


class TestReturn(unittest.TestCase):

    def test_in_keyword(self):
        data = '    RETURN'
        expected = [(T.RETURN_STATEMENT, 'RETURN', 3, 4),
                    (T.EOS, '', 3, 10)]
        self._verify(data, expected)

    def test_in_test(self):
        data = '    RETURN'
        expected = [(T.ERROR, 'RETURN', 3, 4,  'RETURN is not allowed in this context.'),
                    (T.EOS, '', 3, 10)]
        self._verify(data, expected, test=True)

    def test_in_if(self):
        data = '''\
    IF    True
        RETURN    Hello!
    END
'''
        expected = [(T.IF, 'IF', 3, 4),
                    (T.ARGUMENT, 'True', 3, 10),
                    (T.EOS, '', 3, 14),
                    (T.RETURN_STATEMENT, 'RETURN', 4, 8),
                    (T.ARGUMENT, 'Hello!', 4, 18),
                    (T.EOS, '', 4, 24),
                    (T.END, 'END', 5, 4),
                    (T.EOS, '', 5, 7)]
        self._verify(data, expected)

    def test_in_for(self):
            data = '''\
    FOR    ${x}    IN    @{STUFF}
        RETURN    ${x}
    END
'''
            expected = [(T.FOR, 'FOR', 3, 4),
                        (T.VARIABLE, '${x}', 3, 11),
                        (T.FOR_SEPARATOR, 'IN', 3, 19),
                        (T.ARGUMENT, '@{STUFF}', 3, 25),
                        (T.EOS, '', 3, 33),
                        (T.RETURN_STATEMENT, 'RETURN', 4, 8),
                        (T.ARGUMENT, '${x}', 4, 18),
                        (T.EOS, '', 4, 22),
                        (T.END, 'END', 5, 4),
                        (T.EOS, '', 5, 7)]
            self._verify(data, expected)

    def _verify(self, data, expected, test=False):
        if not test:
            header = '*** Keywords ***'
            header_type = T.KEYWORD_HEADER
            name_type = T.KEYWORD_NAME
        else:
            header = '*** Test Cases ***'
            header_type = T.TESTCASE_HEADER
            name_type = T.TESTCASE_NAME
        data = f'{header}\nName\n{data}'
        expected = [(header_type, header, 1, 0),
                    (T.EOS, '', 1, len(header)),
                    (name_type, 'Name', 2, 0),
                    (T.EOS, '', 2, 4)] + expected
        assert_tokens(data, expected, data_only=True)


class TestContinue(unittest.TestCase):

    def test_in_keyword(self):
        data = '    CONTINUE'
        expected = [(T.ERROR, 'CONTINUE', 3, 4,  'CONTINUE is not allowed in this context.'),
                    (T.EOS, '', 3, 12)]
        self._verify(data, expected)

    def test_in_test(self):
        data = '    CONTINUE'
        expected = [(T.ERROR, 'CONTINUE', 3, 4,  'CONTINUE is not allowed in this context.'),
                    (T.EOS, '', 3, 12)]
        self._verify(data, expected, test=True)

    def test_in_if(self):
        data = '''\
    FOR    ${x}    IN    @{STUFF}
        IF    True
            CONTINUE
        END
    END
'''
        expected = [(T.FOR, 'FOR', 3, 4),
                    (T.VARIABLE, '${x}', 3, 11),
                    (T.FOR_SEPARATOR, 'IN', 3, 19),
                    (T.ARGUMENT, '@{STUFF}', 3, 25),
                    (T.EOS, '', 3, 33),
                    (T.IF, 'IF', 4, 8),
                    (T.ARGUMENT, 'True', 4, 14),
                    (T.EOS, '', 4, 18),
                    (T.CONTINUE, 'CONTINUE', 5, 12),
                    (T.EOS, '', 5, 20),
                    (T.END, 'END', 6, 8),
                    (T.EOS, '', 6, 11),
                    (T.END, 'END', 7, 4),
                    (T.EOS, '', 7, 7)]
        self._verify(data, expected)

    def test_in_try(self):
        data = '''\
    FOR    ${x}    IN    @{STUFF}
        TRY
            KW
        EXCEPT
            CONTINUE
        END
    END
'''
        expected = [(T.FOR, 'FOR', 3, 4),
                    (T.VARIABLE, '${x}', 3, 11),
                    (T.FOR_SEPARATOR, 'IN', 3, 19),
                    (T.ARGUMENT, '@{STUFF}', 3, 25),
                    (T.EOS, '', 3, 33),
                    (T.TRY, 'TRY', 4, 8),
                    (T.EOS, '', 4, 11),
                    (T.KEYWORD, 'KW', 5, 12),
                    (T.EOS, '', 5, 14),
                    (T.EXCEPT, 'EXCEPT', 6, 8),
                    (T.EOS, '', 6, 14),
                    (T.CONTINUE, 'CONTINUE', 7, 12),
                    (T.EOS, '', 7, 20),
                    (T.END, 'END', 8, 8),
                    (T.EOS, '', 8, 11),
                    (T.END, 'END', 9, 4),
                    (T.EOS, '', 9, 7)]
        self._verify(data, expected)

    def test_in_for(self):
        data = '''\
    FOR    ${x}    IN    @{STUFF}
        CONTINUE
    END
'''
        expected = [(T.FOR, 'FOR', 3, 4),
                    (T.VARIABLE, '${x}', 3, 11),
                    (T.FOR_SEPARATOR, 'IN', 3, 19),
                    (T.ARGUMENT, '@{STUFF}', 3, 25),
                    (T.EOS, '', 3, 33),
                    (T.CONTINUE, 'CONTINUE', 4, 8),
                    (T.EOS, '', 4, 16),
                    (T.END, 'END', 5, 4),
                    (T.EOS, '', 5, 7)]
        self._verify(data, expected)

    def test_in_while(self):
        data = '''\
    WHILE    ${EXPR}
        CONTINUE
    END
'''
        expected = [(T.WHILE, 'WHILE', 3, 4),
                    (T.ARGUMENT, '${EXPR}', 3, 13),
                    (T.EOS, '', 3, 20),
                    (T.CONTINUE, 'CONTINUE', 4, 8),
                    (T.EOS, '', 4, 16),
                    (T.END, 'END', 5, 4),
                    (T.EOS, '', 5, 7)]
        self._verify(data, expected)

    def _verify(self, data, expected, test=False):
        if not test:
            header = '*** Keywords ***'
            header_type = T.KEYWORD_HEADER
            name_type = T.KEYWORD_NAME
        else:
            header = '*** Test Cases ***'
            header_type = T.TESTCASE_HEADER
            name_type = T.TESTCASE_NAME
        data = f'{header}\nName\n{data}'
        expected = [(header_type, header, 1, 0),
                    (T.EOS, '', 1, len(header)),
                    (name_type, 'Name', 2, 0),
                    (T.EOS, '', 2, 4)] + expected
        assert_tokens(data, expected, data_only=True)


class TestBreak(unittest.TestCase):

    def test_in_keyword(self):
        data = '    BREAK'
        expected = [(T.ERROR, 'BREAK', 3, 4,  'BREAK is not allowed in this context.'),
                    (T.EOS, '', 3, 9)]
        self._verify(data, expected)

    def test_in_test(self):
        data = '    BREAK'
        expected = [(T.ERROR, 'BREAK', 3, 4,  'BREAK is not allowed in this context.'),
                    (T.EOS, '', 3, 9)]
        self._verify(data, expected, test=True)

    def test_in_if(self):
        data = '''\
    FOR    ${x}    IN    @{STUFF}
        IF    True
            BREAK
        END
    END
'''
        expected = [(T.FOR, 'FOR', 3, 4),
                    (T.VARIABLE, '${x}', 3, 11),
                    (T.FOR_SEPARATOR, 'IN', 3, 19),
                    (T.ARGUMENT, '@{STUFF}', 3, 25),
                    (T.EOS, '', 3, 33),
                    (T.IF, 'IF', 4, 8),
                    (T.ARGUMENT, 'True', 4, 14),
                    (T.EOS, '', 4, 18),
                    (T.BREAK, 'BREAK', 5, 12),
                    (T.EOS, '', 5, 17),
                    (T.END, 'END', 6, 8),
                    (T.EOS, '', 6, 11),
                    (T.END, 'END', 7, 4),
                    (T.EOS, '', 7, 7)]
        self._verify(data, expected)

    def test_in_for(self):
        data = '''\
    FOR    ${x}    IN    @{STUFF}
        BREAK
    END
'''
        expected = [(T.FOR, 'FOR', 3, 4),
                    (T.VARIABLE, '${x}', 3, 11),
                    (T.FOR_SEPARATOR, 'IN', 3, 19),
                    (T.ARGUMENT, '@{STUFF}', 3, 25),
                    (T.EOS, '', 3, 33),
                    (T.BREAK, 'BREAK', 4, 8),
                    (T.EOS, '', 4, 13),
                    (T.END, 'END', 5, 4),
                    (T.EOS, '', 5, 7)]
        self._verify(data, expected)

    def test_in_while(self):
        data = '''\
    WHILE    ${EXPR}
        BREAK
    END
'''
        expected = [(T.WHILE, 'WHILE', 3, 4),
                    (T.ARGUMENT, '${EXPR}', 3, 13),
                    (T.EOS, '', 3, 20),
                    (T.BREAK, 'BREAK', 4, 8),
                    (T.EOS, '', 4, 13),
                    (T.END, 'END', 5, 4),
                    (T.EOS, '', 5, 7)]
        self._verify(data, expected)

    def test_in_try(self):
        data = '''\
    FOR    ${x}    IN    @{STUFF}
        TRY
            KW
        EXCEPT
            BREAK
        END
    END
'''
        expected = [(T.FOR, 'FOR', 3, 4),
                    (T.VARIABLE, '${x}', 3, 11),
                    (T.FOR_SEPARATOR, 'IN', 3, 19),
                    (T.ARGUMENT, '@{STUFF}', 3, 25),
                    (T.EOS, '', 3, 33),
                    (T.TRY, 'TRY', 4, 8),
                    (T.EOS, '', 4, 11),
                    (T.KEYWORD, 'KW', 5, 12),
                    (T.EOS, '', 5, 14),
                    (T.EXCEPT, 'EXCEPT', 6, 8),
                    (T.EOS, '', 6, 14),
                    (T.BREAK, 'BREAK', 7, 12),
                    (T.EOS, '', 7, 17),
                    (T.END, 'END', 8, 8),
                    (T.EOS, '', 8, 11),
                    (T.END, 'END', 9, 4),
                    (T.EOS, '', 9, 7)]
        self._verify(data, expected)

    def _verify(self, data, expected, test=False):
        if not test:
            header = '*** Keywords ***'
            header_type = T.KEYWORD_HEADER
            name_type = T.KEYWORD_NAME
        else:
            header = '*** Test Cases ***'
            header_type = T.TESTCASE_HEADER
            name_type = T.TESTCASE_NAME
        data = f'{header}\nName\n{data}'
        expected = [(header_type, header, 1, 0),
                    (T.EOS, '', 1, len(header)),
                    (name_type, 'Name', 2, 0),
                    (T.EOS, '', 2, 4)] + expected
        assert_tokens(data, expected, data_only=True)


class TestVar(unittest.TestCase):

    def test_simple(self):
        data = 'VAR    ${name}    value'
        expected = [
            (T.VAR, 'VAR', 3, 4),
            (T.VARIABLE, '${name}', 3, 11),
            (T.ARGUMENT, 'value', 3, 22),
            (T.EOS, '', 3, 27)
        ]
        self._verify(data, expected)

    def test_equals(self):
        data = 'VAR    ${name}=    value'
        expected = [
            (T.VAR, 'VAR', 3, 4),
            (T.VARIABLE, '${name}=', 3, 11),
            (T.ARGUMENT, 'value', 3, 23),
            (T.EOS, '', 3, 28)
        ]
        self._verify(data, expected)

    def test_multiple_values(self):
        data = 'VAR    @{name}    v1    v2\n...    v3'
        expected = [
            (T.VAR, None, 3, 4),
            (T.VARIABLE, '@{name}', 3, 11),
            (T.ARGUMENT, 'v1', 3, 22),
            (T.ARGUMENT, 'v2', 3, 28),
            (T.ARGUMENT, 'v3', 4, 11),
            (T.EOS, '', 4, 13)
        ]
        self._verify(data, expected)

    def test_no_values(self):
        data = 'VAR    @{name}'
        expected = [
            (T.VAR, 'VAR', 3, 4),
            (T.VARIABLE, '@{name}', 3, 11),
            (T.EOS, '', 3, 18)
        ]
        self._verify(data, expected)

    def test_no_name(self):
        data = 'VAR'
        expected = [
            (T.VAR, 'VAR', 3, 4),
            (T.EOS, '', 3, 7)
        ]
        self._verify(data, expected)

    def test_no_name_with_continuation(self):
        data = 'VAR\n...'
        expected = [
            (T.VAR, 'VAR', 3, 4),
            (T.VARIABLE, '', 4, 7),
            (T.EOS, '', 4, 7)
        ]
        self._verify(data, expected)

    def test_scope(self):
        data = ('VAR    ${name}    value    scope=GLOBAL\n'
                'VAR    @{name}    value    scope=suite\n'
                'VAR    &{name}    value    scope=Test\n')
        expected = [
            (T.VAR, 'VAR', 3, 4),
            (T.VARIABLE, '${name}', 3, 11),
            (T.ARGUMENT, 'value', 3, 22),
            (T.OPTION, 'scope=GLOBAL', 3, 31),
            (T.EOS, '', 3, 43),
            (T.VAR, 'VAR', 4, 4),
            (T.VARIABLE, '@{name}', 4, 11),
            (T.ARGUMENT, 'value', 4, 22),
            (T.OPTION, 'scope=suite', 4, 31),
            (T.EOS, '', 4, 42),
            (T.VAR, 'VAR', 5, 4),
            (T.VARIABLE, '&{name}', 5, 11),
            (T.ARGUMENT, 'value', 5, 22),
            (T.OPTION, 'scope=Test', 5, 31),
            (T.EOS, '', 5, 41)
        ]
        self._verify(data, expected)

    def test_only_one_scope(self):
        data = ('VAR    ${name}    scope=value    scope=GLOBAL\n'
                'VAR    &{name}    scope=value    scope=GLOBAL')
        expected = [
            (T.VAR, 'VAR', 3, 4),
            (T.VARIABLE, '${name}', 3, 11),
            (T.ARGUMENT, 'scope=value', 3, 22),
            (T.OPTION, 'scope=GLOBAL', 3, 37),
            (T.EOS, '', 3, 49),
            (T.VAR, 'VAR', 4, 4),
            (T.VARIABLE, '&{name}', 4, 11),
            (T.ARGUMENT, 'scope=value', 4, 22),
            (T.OPTION, 'scope=GLOBAL', 4, 37),
            (T.EOS, '', 4, 49)
        ]
        self._verify(data, expected)

    def test_separator_with_scalar(self):
        data = 'VAR    ${name}    v1    v2    separator=-'
        expected = [
            (T.VAR, 'VAR', 3, 4),
            (T.VARIABLE, '${name}', 3, 11),
            (T.ARGUMENT, 'v1', 3, 22),
            (T.ARGUMENT, 'v2', 3, 28),
            (T.OPTION, 'separator=-', 3, 34),
            (T.EOS, '', 3, 45)
        ]
        self._verify(data, expected)

    def test_only_one_separator(self):
        data = 'VAR    ${name}    scope=v1    separator=v2    separator=-'
        expected = [
            (T.VAR, 'VAR', 3, 4),
            (T.VARIABLE, '${name}', 3, 11),
            (T.ARGUMENT, 'scope=v1', 3, 22),
            (T.ARGUMENT, 'separator=v2', 3, 34),
            (T.OPTION, 'separator=-', 3, 50),
            (T.EOS, '', 3, 61)
        ]
        self._verify(data, expected)

    def test_no_separator_with_list(self):
        data = 'VAR    @{name}    v1    v2    separator=-'
        expected = [
            (T.VAR, 'VAR', 3, 4),
            (T.VARIABLE, '@{name}', 3, 11),
            (T.ARGUMENT, 'v1', 3, 22),
            (T.ARGUMENT, 'v2', 3, 28),
            (T.ARGUMENT, 'separator=-', 3, 34),
            (T.EOS, '', 3, 45)
        ]
        self._verify(data, expected)

    def test_no_separator_with_dict(self):
        data = 'VAR    &{name}    scope=value    separator=-'
        expected = [
            (T.VAR, 'VAR', 3, 4),
            (T.VARIABLE, '&{name}', 3, 11),
            (T.ARGUMENT, 'scope=value', 3, 22),
            (T.ARGUMENT, 'separator=-', 3, 37),
            (T.EOS, '', 3, 48)
        ]
        self._verify(data, expected)

    def _verify(self, data, expected):
        data = '    ' + '\n    '.join(data.splitlines())
        data = f'*** Test Cases ***\nName\n{data}'
        expected = [(T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
                    (T.EOS, '', 1, 18),
                    (T.TESTCASE_NAME, 'Name', 2, 0),
                    (T.EOS, '', 2, 4)] + expected
        assert_tokens(data, expected, data_only=True)


class TestLanguageConfig(unittest.TestCase):

    def test_lang_as_code(self):
        self._test_explicit_config('fi')
        self._test_explicit_config('F-I')

    def test_lang_as_name(self):
        self._test_explicit_config('Finnish')
        self._test_explicit_config('FINNISH')

    def test_lang_as_Language(self):
        self._test_explicit_config(Language.from_name('fi'))

    def test_lang_as_list(self):
        self._test_explicit_config(['fi', Language.from_name('de')])
        self._test_explicit_config([Language.from_name('fi'), 'de'])

    def test_lang_as_tuple(self):
        self._test_explicit_config(('f-i', Language.from_name('de')))
        self._test_explicit_config((Language.from_name('fi'), 'de'))

    def test_lang_as_Languages(self):
        self._test_explicit_config(Languages('fi'))

    def _test_explicit_config(self, lang):
        data = '''\
*** Asetukset ***
Dokumentaatio    Documentation
'''
        expected = [
            (T.SETTING_HEADER, '*** Asetukset ***', 1, 0),
            (T.EOL, '\n', 1, 17),
            (T.EOS, '', 1, 18),
            (T.DOCUMENTATION, 'Dokumentaatio', 2, 0),
            (T.SEPARATOR, '    ', 2, 13),
            (T.ARGUMENT, 'Documentation', 2, 17),
            (T.EOL, '\n', 2, 30),
            (T.EOS, '', 2, 31),
        ]
        assert_tokens(data, expected, get_tokens, lang=lang)
        assert_tokens(data, expected, get_init_tokens, lang=lang)
        assert_tokens(data, expected, get_resource_tokens, lang=lang)

    def test_per_file_config(self):
        data = '''\
language: pt    not recognized
language: fi
ignored    language: pt
Language:German    # ok!
*** Asetukset ***
Dokumentaatio    Documentation
'''
        expected = [
            (T.COMMENT, 'language: pt', 1, 0),
            (T.SEPARATOR, '    ', 1, 12),
            (T.COMMENT, 'not recognized', 1, 16),
            (T.EOL, '\n', 1, 30),
            (T.EOS, '', 1, 31),
            (T.CONFIG, 'language: fi', 2, 0),
            (T.EOL, '\n', 2, 12),
            (T.EOS, '', 2, 13),
            (T.COMMENT, 'ignored', 3, 0),
            (T.SEPARATOR, '    ', 3, 7),
            (T.COMMENT, 'language: pt', 3, 11),
            (T.EOL, '\n', 3, 23),
            (T.EOS, '', 3, 24),
            (T.CONFIG, 'Language:German', 4, 0),
            (T.SEPARATOR, '    ', 4, 15),
            (T.COMMENT, '# ok!', 4, 19),
            (T.EOL, '\n', 4, 24),
            (T.EOS, '', 4, 25),
            (T.SETTING_HEADER, '*** Asetukset ***', 5, 0),
            (T.EOL, '\n', 5, 17),
            (T.EOS, '', 5, 18),
            (T.DOCUMENTATION, 'Dokumentaatio', 6, 0),
            (T.SEPARATOR, '    ', 6, 13),
            (T.ARGUMENT, 'Documentation', 6, 17),
            (T.EOL, '\n', 6, 30),
            (T.EOS, '', 6, 31),
        ]
        assert_tokens(data, expected, get_tokens)
        lang = Languages()
        assert_tokens(data, expected, get_init_tokens, lang=lang)
        assert_equal(lang.languages,
                     [Language.from_name(lang) for lang in ('en', 'fi', 'de')])

    def test_invalid_per_file_config(self):
        data = '''\
language: in:va:lid
language: bad again    but not recognized as config and ignored
Language: Finnish
*** Asetukset ***
Dokumentaatio    Documentation
'''
        expected = [
            (T.ERROR, 'language: in:va:lid', 1, 0,
             "Invalid language configuration: Language 'in:va:lid' not found "
             "nor importable as a language module."),
            (T.EOL, '\n', 1, 19),
            (T.EOS, '', 1, 20),
            (T.COMMENT, 'language: bad again', 2, 0),
            (T.SEPARATOR, '    ', 2, 19),
            (T.COMMENT, 'but not recognized as config and ignored', 2, 23),
            (T.EOL, '\n', 2, 63),
            (T.EOS, '', 2, 64),
            (T.CONFIG, 'Language: Finnish', 3, 0),
            (T.EOL, '\n', 3, 17),
            (T.EOS, '', 3, 18),
            (T.SETTING_HEADER, '*** Asetukset ***', 4, 0),
            (T.EOL, '\n', 4, 17),
            (T.EOS, '', 4, 18),
            (T.DOCUMENTATION, 'Dokumentaatio', 5, 0),
            (T.SEPARATOR, '    ', 5, 13),
            (T.ARGUMENT, 'Documentation', 5, 17),
            (T.EOL, '\n', 5, 30),
            (T.EOS, '', 5, 31),
        ]
        assert_tokens(data, expected, get_tokens)
        lang = Languages()
        assert_tokens(data, expected, get_init_tokens, lang=lang)
        assert_equal(lang.languages,
                     [Language.from_name(lang) for lang in ('en', 'fi')])


if __name__ == '__main__':
    unittest.main()
