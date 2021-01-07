import unittest

from robot.parsing import Token
from robot.parsing.model.statements import (
    Statement,
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
from robot.utils.asserts import assert_equal


def assert_created_statement(tokens, base_class, **params):
    new_statement = base_class.from_params(**params)
    assert_equal(
        new_statement,
        base_class(tokens)
    )
    assert_equal(
        new_statement,
        base_class.from_tokens(tokens)
    )
    assert_equal(
        new_statement,
        Statement.from_tokens(tokens)
    )


class TestCreateStatementsFromParams(unittest.TestCase):

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
            keyword='Setup Keyword',
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
            keyword='Teardown Keyword',
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
            keyword='Setup Keyword',
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
            keyword='Teardown Keyword',
            args=['${arg1}', '${arg2}']
        )

    def test_TestTemplate(self):
        tokens = [
            Token(Token.TEST_TEMPLATE, 'Test Template'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'Keyword Template'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            TestTemplate,
            keyword='Keyword Template'
        )

    def test_TestTimeout(self):
        tokens = [
            Token(Token.TEST_TIMEOUT, 'Test Timeout'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '1 min'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            TestTimeout,
            timeout='1 min'
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
            keyword='Setup Keyword',
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
            keyword='Teardown Keyword',
            args=['${arg1}']
        )

    def test_LibraryImport(self):
        tokens = [
            Token(Token.LIBRARY, 'Library'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'library_name.py')
        ]
        assert_created_statement(
            tokens + [Token(Token.EOL, '\n')],
            LibraryImport,
            library='library_name.py'
        )

        tokens.extend([
            Token(Token.SEPARATOR, '    '),
            Token(Token.WITH_NAME, 'WITH NAME'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'anothername'),
            Token(Token.EOL, '\n')
        ])
        assert_created_statement(
            tokens,
            LibraryImport,
            library='library_name.py',
            alias='anothername'
        )

    def test_ResourceImport(self):
        tokens = [
            Token(Token.RESOURCE, 'Resource'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'path${/}to${/}resource.robot'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            ResourceImport,
            resource='path${/}to${/}resource.robot'
        )

    def test_VariablesImport(self):
        tokens = [
            Token(Token.VARIABLES, 'Variables'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'variables.py'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            VariablesImport,
            variable_file='variables.py'
        )

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
            variable_file='variables.py',
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
            doc='Example documentation'
        )

        # Documentation    First line
        # ...    Second line
        tokens = [
            Token(Token.DOCUMENTATION, 'Documentation'),
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
            Documentation,
            doc='First line\nSecond line'
        )

        # Test
        #     [Documentation]    First line
        #     ...    Second line
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.DOCUMENTATION, '[Documentation]'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'First line'),
            Token(Token.EOL, '\n'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.CONTINUATION),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'Second line'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Documentation,
            settings_section=False,
            doc='First line\nSecond line'
        )

    def test_Metadata(self):
        tokens = [
            Token(Token.METADATA, 'Metadata'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'Example documentation'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Metadata,
            metadata='Example documentation'
        )

        tokens = [
            Token(Token.METADATA, 'Metadata'),
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
            metadata='First line\nSecond line'
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
            tags=['tag1', 'tag2']
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
            tags=['some tag', 'another_tag']
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
            tags=['some tag', 'another_tag']
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
            keyword='Keyword Name'
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
            timeout='1 min'
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
            keyword='Keyword Call',
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
            Token(Token.FOR, 'FOR'),
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
            for_separator='IN ZIP',
            variables=['${value1}', '${value2}'],
            values=['${list1}', '${list2}'],
            separator='  '
        )

    def test_IfHeader(self):
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
