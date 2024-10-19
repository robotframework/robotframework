import unittest

from robot.api import Token
from robot.parsing.lexer.tokens import ErrorCode, ErrorKind, InvalidTokenError
from robot.utils.asserts import assert_equal, assert_false


class TestToken(unittest.TestCase):

    def test_string_repr(self):
        for token, exp_str, exp_repr in [
            ((Token.ELSE_IF, 'ELSE IF', 6, 4), 'ELSE IF',
             "Token(ELSE_IF, 'ELSE IF', 6, 4)"),
            ((Token.KEYWORD, 'Hyvä', 6, 4), 'Hyvä',
             "Token(KEYWORD, 'Hyvä', 6, 4)"),
            ((Token.ERROR, 'bad value', 6, 4, 'The error.'), 'bad value',
             "Token(ERROR, 'bad value', 6, 4, 'The error.')"),
            (((), '',
              "Token(None, '', -1, -1)"))
        ]:
            token = Token(*token)
            assert_equal(str(token), exp_str)
            assert_equal(repr(token), exp_repr)

    def test_automatic_value(self):
        for typ, value in [(Token.IF, 'IF'),
                           (Token.ELSE_IF, 'ELSE IF'),
                           (Token.ELSE, 'ELSE'),
                           (Token.FOR, 'FOR'),
                           (Token.END, 'END'),
                           (Token.CONTINUATION, '...'),
                           (Token.EOL, '\n'),
                           (Token.AS, 'AS')]:
            assert_equal(Token(typ).value, value)

    def test_set_error(self):
        token = Token(Token.RETURN, 'Hello', 1, 0)
        assert_equal(token.error, None)
        error_token = InvalidTokenError(ErrorKind.ERROR, ErrorCode.SYNTAX_ERROR, 'Bad!')
        token.set_error(error_token)
        assert_equal(token.error, InvalidTokenError(ErrorKind.ERROR, ErrorCode.SYNTAX_ERROR, 'Bad!'))
        assert_equal(token.type, "ERROR")

class TestTokenizeVariables(unittest.TestCase):

    def test_types_that_can_contain_variables(self):
        for token_type in [Token.NAME, Token.ARGUMENT, Token.TESTCASE_NAME,
                           Token.KEYWORD_NAME]:
            token = Token(token_type, 'Nothing to see hear!')
            assert_equal(list(token.tokenize_variables()),
                         [token])
            token = Token(token_type, '${var only}')
            assert_equal(list(token.tokenize_variables()),
                         [Token(Token.VARIABLE, '${var only}')])
            token = Token(token_type, 'Hello, ${var}!', 1, 0)
            assert_equal(list(token.tokenize_variables()),
                         [Token(token_type, 'Hello, ', 1, 0),
                          Token(Token.VARIABLE, '${var}', 1, 7),
                          Token(token_type, '!', 1, 13)])

    def test_types_that_cannot_contain_variables(self):
        for token_type in [Token.VARIABLE, Token.KEYWORD, Token.SEPARATOR]:
            token = Token(token_type, 'Hello, ${var}!', 1, 0)
            assert_equal(list(token.tokenize_variables()),
                         [token])

    def test_tokenize_variables_is_generator(self):
        variables = Token(Token.NAME, 'Hello, ${var}!').tokenize_variables()
        assert_false(isinstance(variables, list))
        assert_equal(iter(variables), variables)

class TestTokenError(unittest.TestCase):

    def test_string_repr(self):
        token_error = InvalidTokenError(ErrorKind.ERROR, ErrorCode.SYNTAX_ERROR, 'Syntax error!')
        expected_str = "InvalidTokenError(ERROR, SYNTAX_ERROR, 'Syntax error!')"
        assert_equal(repr(token_error), expected_str)

    def test_to_string(self):
        error = InvalidTokenError(ErrorKind.ERROR, ErrorCode.SYNTAX_ERROR, 'Something went wrong!')
        assert_equal(str(error), 'Something went wrong!')

    def test_is_warning(self):
        error = InvalidTokenError(ErrorKind.WARNING, ErrorCode.SYNTAX_ERROR, 'Bad!')
        assert_equal(error.is_warning, True)

    def test_as_error(self):
        error = InvalidTokenError.as_error(ErrorCode.SYNTAX_ERROR, 'Something went wrong!')
        assert_equal(error, InvalidTokenError(ErrorKind.ERROR, ErrorCode.SYNTAX_ERROR, 'Something went wrong!'))

    def test_as_warning(self):
        error = InvalidTokenError.as_warning(ErrorCode.RETURN_SETTING_DEPRECATED, 'Deprecated!')
        assert_equal(error, InvalidTokenError(ErrorKind.WARNING, ErrorCode.RETURN_SETTING_DEPRECATED, 'Deprecated!'))


if __name__ == '__main__':
    unittest.main()
