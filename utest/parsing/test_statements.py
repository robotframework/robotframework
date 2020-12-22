import unittest

from robot.parsing import Token
from robot.parsing.model.statements import (
    Statement,
    TestCaseName,
    IfHeader,
    ElseHeader,
    ElseIfHeader,
    End,
    Comment,
    EmptyLine
)
from robot.utils.asserts import assert_equal


def assert_statement(model, expected):
    assert_equal(model._fields, ('type', 'tokens'))
    assert_equal(model.type, expected.type)
    assert_equal(len(model.tokens), len(expected.tokens))
    for m, e in zip(model.tokens, expected.tokens):
        assert_equal(m, e, formatter=repr)
    assert_equal(model._attributes, ('lineno', 'col_offset', 'end_lineno',
                                     'end_col_offset', 'errors'))
    assert_equal(model.lineno, expected.tokens[0].lineno)
    assert_equal(model.col_offset, expected.tokens[0].col_offset)
    assert_equal(model.end_lineno, expected.tokens[-1].lineno)
    assert_equal(model.end_col_offset, expected.tokens[-1].end_col_offset)
    assert_equal(model.errors, expected.errors)


def assert_created_statement(tokens, new_statement, base_class):
    assert_statement(
        new_statement,
        base_class(tokens)
    )
    assert_statement(
        new_statement,
        base_class.from_tokens(tokens)
    )
    assert_statement(
        new_statement,
        Statement.from_tokens(tokens)
    )


class TestCreateStatementsFromParams:
    def test_SectionHeader(self):
        tokens = [Token(Token.TESTCASE_NAME, 'Example test case name'), Token(Token.EOL, '\n')]
        assert_created_statement(
            tokens,
            TestCaseName.from_params(name='Example test case name'),
            TestCaseName
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
            IfHeader.from_params(condition='${var} not in [@{list}]'),
            IfHeader
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
            ElseIfHeader.from_params(condition='${var} not in [@{list}]'),
            ElseIfHeader
        )

    def test_ElseHeader(self):
        tokens = [
            Token(Token.SEPARATOR, '    '),
            Token(Token.ELSE),
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            ElseHeader.from_params(),
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
            End.from_params(),
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
            Comment.from_params(comment='# example comment'),
            Comment
        )

    def test_EmptyLine(self):
        tokens = [
            Token(Token.EOL, '\n')
        ]
        assert_created_statement(
            tokens,
            EmptyLine.from_params('\n'),
            EmptyLine
        )


if __name__ == '__main__':
    unittest.main()
