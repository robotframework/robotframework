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
    ForceTags,
    DefaultTags,
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

    def test_SectionHeader(self):
        tokens = [Token(Token.TESTCASE_NAME, 'Example test case name'), Token(Token.EOL, '\n')]
        assert_created_statement(
            tokens,
            TestCaseName,
            name='Example test case name'
        )

    def test_LibraryImport(self):
        tokens = [Token(Token.LIBRARY), Token(Token.SEPARATOR, '    '), Token(Token.NAME, 'library_name.py')]
        assert_created_statement(
            tokens + [Token(Token.EOL, '\n')],
            LibraryImport,
            library='library_name.py'
        )

        tokens.extend([
            Token(Token.SEPARATOR, '    '),
            Token(Token.WITH_NAME),
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
            Token(Token.RESOURCE),
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
            Token(Token.VARIABLES),
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
            Token(Token.VARIABLES),
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
            Token(Token.DOCUMENTATION),
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
            Token(Token.DOCUMENTATION),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'First line'),
            Token(Token.EOL, '\n'),
            Token(Token.CONTINUATION, '...'),
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
            Token(Token.CONTINUATION, '...'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'Second line'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            Documentation,
            test_documentation=True,
            doc='First line\nSecond line'
        )

    def test_Metadata(self):
        tokens = [
            Token(Token.METADATA),
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
            Token(Token.METADATA),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'First line'),
            Token(Token.EOL, '\n'),
            Token(Token.CONTINUATION, '...'),
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
            Token(Token.FORCE_TAGS),
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
            Token(Token.DEFAULT_TAGS),
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
