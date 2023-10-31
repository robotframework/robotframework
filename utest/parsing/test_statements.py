import unittest

from robot.parsing.model.statements import *
from robot.parsing import Token
from robot.utils.asserts import assert_equal, assert_true
from robot.utils import type_name


def assert_created_statement(tokens, base_class, **params):
    statement = base_class.from_params(**params)
    assert_statements(
        statement,
        base_class(tokens)
    )
    assert_statements(
        statement,
        base_class.from_tokens(tokens)
    )
    assert_statements(
        statement,
        Statement.from_tokens(tokens)
    )
    if len(set(id(t) for t in statement.tokens)) != len(tokens):
        lines = '\n'.join(f'{i:18}{t}' for i, t in
                          [('ID', 'TOKEN')] +
                          [(str(id(t)), repr(t)) for t in statement.tokens])
        raise AssertionError(f'Tokens should not be reused!\n\n{lines}')
    return statement


def compare_statements(first, second):
    return (isinstance(first, type(second))
            and first.tokens == second.tokens
            and first.errors == second.errors)


def assert_statements(st1, st2):
    assert_equal(len(st1), len(st2),
                 f'Statement lengths are not equal:\n'
                 f'{len(st1)} for {st1}\n'
                 f'{len(st2)} for {st2}')
    for t1, t2 in zip(st1, st2):
        assert_equal(t1, t2, formatter=repr)
    assert_true(compare_statements(st1, st2),
                f'Statements are not equal:\n'
                f'{st1} {type_name(st1)}\n'
                f'{st2} {type_name(st2)}')


class TestStatementFromTokens(unittest.TestCase):

    def test_keyword_call_with_assignment(self):
        tokens = [Token(Token.SEPARATOR, '  '),
                  Token(Token.ASSIGN, '${var}'),
                  Token(Token.SEPARATOR, '  '),
                  Token(Token.KEYWORD, 'Keyword'),
                  Token(Token.SEPARATOR, '  '),
                  Token(Token.ARGUMENT, 'arg'),
                  Token(Token.EOL)]
        assert_statements(Statement.from_tokens(tokens), KeywordCall(tokens))

    def test_inline_if_with_assignment(self):
        tokens = [Token(Token.SEPARATOR, '  '),
                  Token(Token.ASSIGN, '${var}'),
                  Token(Token.SEPARATOR, '  '),
                  Token(Token.INLINE_IF, 'IF'),
                  Token(Token.SEPARATOR, '  '),
                  Token(Token.ARGUMENT, 'True'),
                  Token(Token.EOL)]
        assert_statements(Statement.from_tokens(tokens), InlineIfHeader(tokens))

    def test_assign_only(self):
        tokens = [Token(Token.SEPARATOR, '  '),
                  Token(Token.ASSIGN, '${var}'),
                  Token(Token.EOL)]
        assert_statements(Statement.from_tokens(tokens), KeywordCall(tokens))


class TestCreateStatementsFromParams(unittest.TestCase):

    def test_Statement(self):
        self.assertRaises(NotImplementedError, Statement.from_params)

    def test_SectionHeader(self):
        headers = {
            Token.SETTING_HEADER: 'Settings',
            Token.VARIABLE_HEADER: 'Variables',
            Token.TESTCASE_HEADER: 'Test Cases',
            Token.TASK_HEADER: 'Tasks',
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

    def test_KeywordTags(self):
        # Keyword Tags    first    second
        tokens = [
            Token(Token.KEYWORD_TAGS, 'Keyword Tags'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'first'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'second'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            KeywordTags,
            values=['first', 'second']
        )

    def test_Variable(self):
        # ${variable_name}  {'a': 4, 'b': 'abc'}
        tokens = [
            Token(Token.VARIABLE, '${variable_name}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, "{'a': 4, 'b': 'abc'}"),
            Token(Token.EOL)
        ]
        assert_created_statement(
            tokens,
            Variable,
            name='${variable_name}',
            value="{'a': 4, 'b': 'abc'}"
        )
        # ${x}    a    b    separator=-
        tokens = [
            Token(Token.VARIABLE, '${x}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'a'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'b'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.OPTION, 'separator=-'),
            Token(Token.EOL)
        ]
        assert_created_statement(
            tokens,
            Variable,
            name='${x}',
            value=['a', 'b'],
            value_separator='-'
        )
        # ${var}    first    second    third
        # @{var}    first    second    third
        # &{var}    first    second    third
        for name in ['${var}', '@{var}', '&{var}']:
            tokens = [
                Token(Token.VARIABLE, name),
                Token(Token.SEPARATOR, '    '),
                Token(Token.ARGUMENT, 'first'),
                Token(Token.SEPARATOR, '    '),
                Token(Token.ARGUMENT, 'second'),
                Token(Token.SEPARATOR, '    '),
                Token(Token.ARGUMENT, 'third'),
                Token(Token.EOL)
            ]
            assert_created_statement(
                tokens,
                Variable,
                name=name,
                value=['first', 'second', 'third']
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

        # Library    library_name.py    AS    anothername
        tokens = [
            Token(Token.LIBRARY, 'Library'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.NAME, 'library_name.py'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.AS),
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
        doc = assert_created_statement(
            tokens,
            Documentation,
            value='Example documentation'
        )
        assert_equal(doc.value, 'Example documentation')

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
            Token(Token.ARGUMENT, ''),
            Token(Token.EOL),
            Token(Token.CONTINUATION),
            Token(Token.SEPARATOR, '              '),
            Token(Token.ARGUMENT, 'Second paragraph.'),
            Token(Token.EOL),
        ]
        doc = assert_created_statement(
            tokens,
            Documentation,
            value='First line.\nSecond line aligned.\n\nSecond paragraph.'
        )
        assert_equal(doc.value, 'First line.\nSecond line aligned.\n\nSecond paragraph.')

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
            Token(Token.ARGUMENT, ''),
            Token(Token.EOL),
            Token(Token.SEPARATOR, '  '),
            Token(Token.CONTINUATION),
            Token(Token.SEPARATOR, '                  '),
            Token(Token.ARGUMENT, 'Second paragraph.'),
            Token(Token.EOL),
        ]
        doc = assert_created_statement(
            tokens,
            Documentation,
            value='First line.\nSecond line aligned.\n\nSecond paragraph.\n',
            indent='  ',
            separator='      ',
            settings_section=False
        )
        assert_equal(doc.value, 'First line.\nSecond line aligned.\n\nSecond paragraph.')

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
            Token(Token.TEST_TAGS, 'Test Tags'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'some tag'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'another_tag'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            TestTags,
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

    def test_ReturnSetting(self):
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
            ReturnSetting,
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
            assign=['${value1}', '${value2}'],
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

    def test_InlineIfHeader(self):
        # Test/Keyword
        #     IF    $x > 0
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.INLINE_IF),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '$x > 0')
        ]
        assert_created_statement(
            tokens,
            InlineIfHeader,
            condition='$x > 0'
        )

    def test_InlineIfHeader_with_assign(self):
        # Test/Keyword
        #     ${y} =    IF    $x > 0
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.ASSIGN, '${y}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.INLINE_IF),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '$x > 0')
        ]
        assert_created_statement(
            tokens,
            InlineIfHeader,
            condition='$x > 0',
            assign=['${y}']
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

    def test_TryHeader(self):
        # TRY
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.TRY),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            TryHeader
        )

    def test_ExceptHeader(self):
        # EXCEPT
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.EXCEPT),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            ExceptHeader
        )
        # EXCEPT    one
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.EXCEPT),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'one'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            ExceptHeader,
            patterns=['one']
        )
        # EXCEPT    one    two    AS    ${var}
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.EXCEPT),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'one'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'two'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.AS, 'AS'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.VARIABLE, '${var}'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            ExceptHeader,
            patterns=['one', 'two'],
            assign='${var}'
        )
        # EXCEPT    Example: *    type=glob
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.EXCEPT),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'Example: *'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.OPTION, 'type=glob'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            ExceptHeader,
            patterns=['Example: *'],
            type='glob'
        )
        # EXCEPT    Error \\d    (x|y)    type=regexp    AS    ${var}
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.EXCEPT),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'Error \\d'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '(x|y)'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.OPTION, 'type=regexp'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.AS, 'AS'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.VARIABLE, '${var}'),
            Token(Token.EOL, '\n')]
        assert_created_statement(
            tokens,
            ExceptHeader,
            patterns=['Error \\d', '(x|y)'],
            type='regexp',
            assign='${var}'
        )

    def test_FinallyHeader(self):
        # FINALLY
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.FINALLY),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            FinallyHeader
        )

    def test_WhileHeader(self):
        # WHILE    $cond
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.WHILE),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '$cond'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            WhileHeader,
            condition='$cond'
        )
        # WHILE    $cond    limit=100s
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.WHILE),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '$cond'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.OPTION, 'limit=100s'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            WhileHeader,
            condition='$cond',
            limit='100s'
        )
        # WHILE    $cond    limit=10    on_limit_message=Error message
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.WHILE),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, '$cond'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.OPTION, 'limit=10'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.OPTION, 'on_limit_message=Error message'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            WhileHeader,
            condition='$cond',
            limit='10',
            on_limit_message='Error message'
        )

    def test_End(self):
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.END),
            Token(Token.EOL)
        ]
        assert_created_statement(
            tokens,
            End
        )

    def test_Var(self):
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.VAR),
            Token(Token.SEPARATOR, '    '),
            Token(Token.VARIABLE, '${name}'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'value'),
            Token(Token.EOL)
        ]
        var = assert_created_statement(
            tokens,
            Var,
            name='${name}',
            value='value'
        )
        assert_equal(var.name, '${name}')
        assert_equal(var.value, ('value',))
        assert_equal(var.scope, None)
        assert_equal(var.separator, None)
        tokens[-1:-1] = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'value 2'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.OPTION, 'scope=SUITE'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.OPTION, r'separator=\n'),
        ]
        var = assert_created_statement(
            tokens,
            Var,
            name='${name}',
            value=('value', 'value 2'),
            scope='SUITE',
            value_separator=r'\n'
        )
        assert_equal(var.name, '${name}')
        assert_equal(var.value, ('value', 'value 2'))
        assert_equal(var.scope, 'SUITE')
        assert_equal(var.separator, r'\n')

    def test_ReturnStatement(self):
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.RETURN_STATEMENT),
            Token(Token.EOL)
        ]
        assert_created_statement(tokens, ReturnStatement)
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.RETURN_STATEMENT, 'RETURN'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'x'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(tokens, ReturnStatement, values=('x',))

    def test_Break(self):
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.BREAK),
            Token(Token.EOL)
        ]
        assert_created_statement(tokens, Break)

    def test_Continue(self):
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.CONTINUE),
            Token(Token.EOL)
        ]
        assert_created_statement(tokens, Continue)

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
