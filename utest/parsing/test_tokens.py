import unittest

from robot.utils.asserts import assert_equal, assert_false

from robot.api import Token


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


if __name__ == '__main__':
    unittest.main()
