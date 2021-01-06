import unittest

from robot.parsing import Token
from robot.parsing.model.statements import (
    Statement,
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

    def test_ForceTags(self):
        tokens = [
            Token(Token.FORCE_TAGS),
            Token(Token.ARGUMENT, 'some tag'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'another_tag'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            ForceTags,
            tags=['some tag', 'ąętag']
        )

    def test_DefaultTags(self):
        tokens = [
            Token(Token.DEFAULT_TAGS),
            Token(Token.ARGUMENT, 'some tag'),
            Token(Token.SEPARATOR, '    '),
            Token(Token.ARGUMENT, 'ąętag'),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            DefaultTags,
            tags=['some tag', 'ąętag']
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
