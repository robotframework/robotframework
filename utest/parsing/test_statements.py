import unittest

from robot.parsing import Token
from robot.parsing.model.statements import (
    Statement,
    SectionHeader,
    LibraryImport,
    ResourceImport,
    VariablesImport,
    Documentation,
    Metadata,
    Tags,
    TestCaseName,
    KeywordName,
    ForceTags,
    DefaultTags,
    SuiteSetup,
    SuiteTeardown,
    TestSetup,
    TestTeardown,
    TestTemplate,
    TestTimeout,
    Variable,
    Setup,
    Teardown,
    Template,
    Timeout,
    Arguments,
    Return,
    KeywordCall,
    TemplateArguments,
    ForHeader,
    IfHeader,
    ElseHeader,
    ElseIfHeader,
    End,
    Comment,
    EmptyLine
)
from robot.utils.asserts import assert_equal, assert_true
from robot.utils import type_name


def assert_created_statement(tokens, base_class, **params):
    new_statement = base_class.from_params(**params)
    assert_statements(
        new_statement,
        base_class(tokens)
    )
    assert_statements(
        new_statement,
        base_class.from_tokens(tokens)
    )
    assert_statements(
        new_statement,
        Statement.from_tokens(tokens)
    )


def compare_statements(first, second):
    return (isinstance(first, type(second))
            and first.tokens == second.tokens
            and first.errors == second.errors)


def assert_statements(st1, st2):
    for t1, t2 in zip(st1, st2):
        assert_equal(t1, t2, formatter=repr)
    assert_true(
        compare_statements(st1, st2),
        'Statements are not equal. %s (%s) != %s (%s)' % (st1, type_name(st1),
                                                          st2, type_name(st2))
    )
    assert_equal(len(st1), len(st2))


class TestCreateStatementsFromParams(unittest.TestCase):

    def test_Statement(self):
        self.assertRaises(NotImplementedError, Statement.from_params)

    def test_SectionHeader(self):
        headers = {
            Token.SETTING_HEADER: 'Settings',
            Token.VARIABLE_HEADER: 'Variables',
            Token.TESTCASE_HEADER: 'Test Cases',
            Token.KEYWORD_HEADER: 'Keywords',
            Token.COMMENT_HEADER: 'Comments'
        }
        for token_type, name in headers.items():
            tokens = [
                Token(token_type, '*** %s ***' % name),
                Token(Token.EOL, '\n')
            ]
            assert_created_statement(
                tokens,
                SectionHeader,
                type=token_type,
            )
            assert_created_statement(
                tokens,
                SectionHeader,
                type=token_type,
                name=name
            )
            assert_created_statement(
                tokens,
                SectionHeader,
                type=token_type,
                name='*** %s ***' % name
            )

    def test_SuiteSetup(self):
        # Suite Setup    Setup Keyword    ${arg1}    ${arg2}
        tokens = [
            Token(Token.SUITE_SETUP, 'Suite Setup'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'Setup Keyword'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg1}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg2}'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            SuiteSetup,
            name='Setup Keyword',
            args=['${arg1}', '${arg2}']
        )

    def test_SuiteTeardown(self):
        # Suite Teardown    Teardown Keyword    ${arg1}    ${arg2}
        tokens = [
            Token(Token.SUITE_TEARDOWN, 'Suite Teardown'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'Teardown Keyword'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg1}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg2}'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            SuiteTeardown,
            name='Teardown Keyword',
            args=['${arg1}', '${arg2}']
        )

    def test_TestSetup(self):
        # Test Setup    Setup Keyword    ${arg1}    ${arg2}
        tokens = [
            Token(Token.TEST_SETUP, 'Test Setup'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'Setup Keyword'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg1}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg2}'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            TestSetup,
            name='Setup Keyword',
            args=['${arg1}', '${arg2}']
        )

    def test_TestTeardown(self):
        # Test Teardown    Teardown Keyword    ${arg1}    ${arg2}
        tokens = [
            Token(Token.TEST_TEARDOWN, 'Test Teardown'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'Teardown Keyword'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg1}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg2}'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            TestTeardown,
            name='Teardown Keyword',
            args=['${arg1}', '${arg2}']
        )

    def test_TestTemplate(self):
        # *** Settings ***
        # Test Template    Keyword Template
        tokens = [
            Token(Token.TEST_TEMPLATE, 'Test Template'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'Keyword Template'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            TestTemplate,
            value='Keyword Template'
        )

    def test_TestTimeout(self):
        # *** Settings ***
        # Test Timeout    1 min
        tokens = [
            Token(Token.TEST_TIMEOUT, 'Test Timeout'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '1 min'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            TestTimeout,
            value='1 min'
        )

    def test_Variable(self):
        # ${variable_name}  {'a': 4, 'b': 'abc'}
        tokens = [
            Token(Token.VARIABLE, '${variable_name}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, "{'a': 4, 'b': 'abc'}"),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Variable,
            name='${variable_name}',
            value="{'a': 4, 'b': 'abc'}"
        )

    def test_TestCaseName(self):
        tokens = [Token(Token.TESTCASE_NAME, 'Example test case name'), Token(Token.EOL, '\n')]
        assert_created_statement(
            tokens,
            TestCaseName,
            name='Example test case name'
        )

    def test_KeywordName(self):
        tokens = [Token(Token.KEYWORD_NAME, 'Keyword Name With ${embedded} Var'), Token(Token.EOL, '\n')]
        assert_created_statement(
            tokens,
            KeywordName,
            name='Keyword Name With ${embedded} Var'
        )

    def test_Setup(self):
        # Test
        #     [Setup]    Setup Keyword    ${arg1}
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.SETUP, '[Setup]'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'Setup Keyword'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg1}'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Setup,
            name='Setup Keyword',
            args=['${arg1}']
        )

    def test_Teardown(self):
        # Test
        #     [Teardown]    Teardown Keyword    ${arg1}
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.TEARDOWN, '[Teardown]'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'Teardown Keyword'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg1}'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Teardown,
            name='Teardown Keyword',
            args=['${arg1}']
        )

    def test_LibraryImport(self):
        # Library    library_name.py
        tokens = [
            Token(Token.LIBRARY, 'Library'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'library_name.py'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            LibraryImport,
            name='library_name.py'
        )

        # Library    library_name.py    127.0.0.1    8080
        tokens = [
            Token(Token.LIBRARY, 'Library'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'library_name.py'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '127.0.0.1'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '8080'),
            Token(Token.EOL, '\n')
        ]

        # Library    library_name.py    WITH NAME    anothername
        tokens = [
            Token(Token.LIBRARY, 'Library'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'library_name.py'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.WITH_NAME),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'anothername'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            LibraryImport,
            name='library_name.py',
            alias='anothername'
        )

    def test_ResourceImport(self):
        # Resource    path${/}to${/}resource.robot
        tokens = [
            Token(Token.RESOURCE, 'Resource'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'path${/}to${/}resource.robot'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            ResourceImport,
            name='path${/}to${/}resource.robot'
        )

    def test_VariablesImport(self):
        # Variables    variables.py
        tokens = [
            Token(Token.VARIABLES, 'Variables'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'variables.py'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            VariablesImport,
            name='variables.py'
        )

        # Variables    variables.py    arg1    2
        tokens = [
            Token(Token.VARIABLES, 'Variables'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'variables.py'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'arg1'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '2'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            VariablesImport,
            name='variables.py',
            args=['arg1', '2']
        )

    def test_Documentation(self):
        # Documentation    Example documentation
        tokens = [
            Token(Token.DOCUMENTATION, 'Documentation'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'Example documentation'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Documentation,
            value='Example documentation'
        )

        # Documentation    First line.
        # ...              Second line aligned.
        # ...
        # ...              Second paragraph.
        tokens = [
            Token(Token.DOCUMENTATION, 'Documentation'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'First line.'),
            Token(Token.EOL),
            Token(Token.CONTINUATION),
            Token(Token.SEPARATOR, '              '),
            Token(Token.ARGUMENT, 'Second line aligned.'),
            Token(Token.EOL),
            Token(Token.CONTINUATION),
            Token(Token.EOL),
            Token(Token.CONTINUATION),
            Token(Token.SEPARATOR, '              '),
            Token(Token.ARGUMENT, 'Second paragraph.'),
            Token(Token.EOL),
        ]
        assert_created_statement(
            tokens,
            Documentation,
            value='First line.\nSecond line aligned.\n\nSecond paragraph.'
        )

        # Test/Keyword
        #     [Documentation]      First line
        #     ...                  Second line aligned
        #     ...
        #     ...                  Second paragraph.
        tokens = [
            Token(Token.SEPARATOR, '  '),
            Token(Token.DOCUMENTATION, '[Documentation]'),
            Token(Token.SEPARATOR, '      '),
            Token(Token.ARGUMENT, 'First line.'),
            Token(Token.EOL),
            Token(Token.SEPARATOR, '  '),
            Token(Token.CONTINUATION),
            Token(Token.SEPARATOR, '                  '),
            Token(Token.ARGUMENT, 'Second line aligned.'),
            Token(Token.EOL),
            Token(Token.SEPARATOR, '  '),
            Token(Token.CONTINUATION),
            Token(Token.EOL),
            Token(Token.SEPARATOR, '  '),
            Token(Token.CONTINUATION),
            Token(Token.SEPARATOR, '                  '),
            Token(Token.ARGUMENT, 'Second paragraph.'),
            Token(Token.EOL),
        ]
        assert_created_statement(
            tokens,
            Documentation,
            value='First line.\nSecond line aligned.\n\nSecond paragraph.\n',
            indent='  ',
            separator='      ',
            settings_section=False
        )

    def test_Metadata(self):
        tokens = [
            Token(Token.METADATA, 'Metadata'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'Key'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'Value'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Metadata,
            name='Key',
            value='Value'
        )

        tokens = [
            Token(Token.METADATA, 'Metadata'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'Key'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'First line'),
            Token(Token.EOL, '\n'),
            Token(Token.CONTINUATION),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'Second line'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Metadata,
            name='Key',
            value='First line\nSecond line'
        )

    def test_Tags(self):
        # Test/Keyword
        #     [Tags]    tag1    tag2
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.TAGS, '[Tags]'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'tag1'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'tag2'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Tags,
            values=['tag1', 'tag2']
        )

    def test_ForceTags(self):
        tokens = [
            Token(Token.FORCE_TAGS, 'Force Tags'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'some tag'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'another_tag'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            ForceTags,
            values=['some tag', 'another_tag']
        )

    def test_DefaultTags(self):
        tokens = [
            Token(Token.DEFAULT_TAGS, 'Default Tags'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'some tag'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'another_tag'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            DefaultTags,
            values=['some tag', 'another_tag']
        )

    def test_Template(self):
        # Test
        #     [Template]  Keyword Name
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.TEMPLATE, '[Template]'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'Keyword Name'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Template,
            value='Keyword Name'
        )

    def test_Timeout(self):
        # Test
        #     [Timeout]  1 min
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.TIMEOUT, '[Timeout]'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '1 min'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Timeout,
            value='1 min'
        )

    def test_Arguments(self):
        # Keyword
        #     [Arguments]    ${arg1}    ${arg2}=4
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENTS, '[Arguments]'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg1}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg2}=4'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Arguments,
            args=['${arg1}', '${arg2}=4']
        )

    def test_Return(self):
        # Keyword
        #     [Return]    ${arg1}    ${arg2}=4
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.RETURN, '[Return]'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg1}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg2}=4'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Return,
            args=['${arg1}', '${arg2}=4']
        )

    def test_KeywordCall(self):
        # Test
        #     ${return1}    ${return2}    Keyword Call    ${arg1}    ${arg2}
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.ASSIGN, '${return1}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ASSIGN, '${return2}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.KEYWORD, 'Keyword Call'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg1}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg2}'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            KeywordCall,
            name='Keyword Call',
            assign=['${return1}', '${return2}'],
            args=['${arg1}', '${arg2}']
        )

    def test_TemplateArguments(self):
        # Test
        #     [Template]   Templated Keyword
        #     ${arg1}    2
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${arg1}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '2'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            TemplateArguments,
            args=['${arg1}', '2']
        )

    def test_ForHeader(self):
        # Keyword
        #     FOR  ${value1}  ${value2}  IN ZIP  ${list1}  ${list2}
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.FOR),
            Token(Token.SEPARATOR, '  '),
            Token(Token.VARIABLE, '${value1}'),
            Token(Token.SEPARATOR, '  '),
            Token(Token.VARIABLE, '${value2}'),
            Token(Token.SEPARATOR, '  '),
            Token(Token.FOR_SEPARATOR, 'IN ZIP'),
            Token(Token.SEPARATOR, '  '),
            Token(Token.ARGUMENT, '${list1}'),
            Token(Token.SEPARATOR, '  '),
            Token(Token.ARGUMENT, '${list2}'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            ForHeader,
            flavor='IN ZIP',
            variables=['${value1}', '${value2}'],
            values=['${list1}', '${list2}'],
            separator='  '
        )

    def test_IfHeader(self):
        # Test/Keyword
        #     IF    ${var} not in [@{list}]
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.IF),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${var} not in [@{list}]'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            IfHeader,
            condition='${var} not in [@{list}]'
        )

    def test_ElseIfHeader(self):
        # Test/Keyword
        #     ELSE IF    ${var} not in [@{list}]
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.ELSE_IF),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '${var} not in [@{list}]'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            ElseIfHeader,
            condition='${var} not in [@{list}]'
        )

    def test_ElseHeader(self):
        # Test/Keyword
        #     ELSE
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.ELSE),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            ElseHeader
        )

    def test_End(self):
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.END),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            End
        )

    def test_Comment(self):
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.COMMENT, '# example comment'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Comment,
            comment='# example comment'
        )

    def test_EmptyLine(self):
        tokens = [
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            EmptyLine,
            eol='\n'
        )


if __name__ == '__main__':
    unittest.main()
