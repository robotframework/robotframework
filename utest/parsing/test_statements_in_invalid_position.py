import unittest

from robot.parsing import get_model, Token
from robot.parsing.model.statements import ReturnStatement

from parsing_test_utils import assert_model, RemoveNonDataTokensVisitor


def remove_non_data_nodes_and_assert(node, expected, data_only):
    if not data_only:
        RemoveNonDataTokensVisitor().visit(node)
    assert_model(node, expected)


class TestReturn(unittest.TestCase):

    def test_in_test_case_body(self):
        for data_only in [True, False]:
            with self.subTest(data_only=data_only):
                model = get_model('''\
*** Test Cases ***
Example
    RETURN''', data_only=data_only)
                node = model.sections[0].body[0].body[0]
                expected = ReturnStatement(
                    [Token(Token.RETURN_STATEMENT, 'RETURN', 3, 4)],
                    errors=('RETURN can only be used inside a user keyword.',)
                )
                remove_non_data_nodes_and_assert(node, expected, data_only)

    def test_in_test_case_body_inside_for(self):
        for data_only in [True, False]:
            with self.subTest(data_only=data_only):
                model = get_model('''\
*** Test Cases ***
Example
    FOR    ${i}    IN    1    2
        RETURN
    END
        ''', data_only=data_only)
                node = model.sections[0].body[0].body[0].body[0]
                expected = ReturnStatement(
                    [Token(Token.RETURN_STATEMENT, 'RETURN', 4, 8)],
                    errors=('RETURN can only be used inside a user keyword.',)
                )
                remove_non_data_nodes_and_assert(node, expected, data_only)

    def test_in_test_case_body_inside_while(self):
        for data_only in [True, False]:
            with self.subTest(data_only=data_only):
                model = get_model('''\
*** Test Cases ***
Example
    WHILE    True
        RETURN
    END
        ''', data_only=data_only)
                node = model.sections[0].body[0].body[0].body[0]
                expected = ReturnStatement(
                    [Token(Token.RETURN_STATEMENT, 'RETURN', 4, 8)],
                    errors=('RETURN can only be used inside a user keyword.',)
                )
                remove_non_data_nodes_and_assert(node, expected, data_only)

    def test_in_test_case_body_inside_if_else(self):
        for data_only in [True, False]:
            with self.subTest(data_only=data_only):
                model = get_model('''\
*** Test Cases ***
Example
    IF    True
        RETURN
    ELSE IF    False
        RETURN
    ELSE
        RETURN
    END
        ''', data_only=data_only)
                ifroot = model.sections[0].body[0].body[0]
                node = ifroot.body[0]
                expected = ReturnStatement(
                    [Token(Token.RETURN_STATEMENT, 'RETURN', 4, 8)],
                    errors=('RETURN can only be used inside a user keyword.',)
                )
                remove_non_data_nodes_and_assert(node, expected, data_only)
                expected.tokens[0].lineno = 6
                remove_non_data_nodes_and_assert(ifroot.orelse.body[0], expected, data_only)
                expected.tokens[0].lineno = 8
                remove_non_data_nodes_and_assert(ifroot.orelse.orelse.body[0], expected, data_only)

    def test_in_test_case_body_inside_try_except(self):
        for data_only in [True, False]:
            with self.subTest(data_only=data_only):
                model = get_model('''\
*** Test Cases ***
Example
    TRY
        RETURN
    EXCEPT
        RETURN
    ELSE
        RETURN
    FINALLY
        RETURN
    END
        ''', data_only=data_only)
                tryroot = model.sections[0].body[0].body[0]
                node = tryroot.body[0]
                expected = ReturnStatement(
                    [Token(Token.RETURN_STATEMENT, 'RETURN', 4, 8)],
                    errors=('RETURN can only be used inside a user keyword.',)
                )
                remove_non_data_nodes_and_assert(node, expected, data_only)
                expected.tokens[0].lineno = 6
                remove_non_data_nodes_and_assert(tryroot.next.body[0], expected, data_only)
                expected.tokens[0].lineno = 8
                remove_non_data_nodes_and_assert(tryroot.next.next.body[0], expected, data_only)
                expected.tokens[0].lineno = 10
                remove_non_data_nodes_and_assert(tryroot.next.next.next.body[0], expected, data_only)

    def test_in_finally_in_uk(self):
        for data_only in [True, False]:
            with self.subTest(data_only=data_only):
                model = get_model('''\
*** Keywords ***
Example
    TRY
        No operation
    EXCEPT
        No operation
    FINALLY
        RETURN
    END
        ''', data_only=data_only)
                node = model.sections[0].body[0].body[0].next.next.body[0]
                expected = ReturnStatement(
                    [Token(Token.RETURN_STATEMENT, 'RETURN', 8, 8)],
                    errors=('RETURN cannot be used in FINALLY branch.',)
                )
                remove_non_data_nodes_and_assert(node, expected, data_only)


def test_in_nested_finally_in_uk(self):
    for data_only in [True, False]:
        with self.subTest(data_only=data_only):
            model = get_model('''\
*** Keywords ***
Example
    IF    True
        TRY
            No operation
        EXCEPT
            No operation
        FINALLY
            RETURN
        END
    END
        ''', data_only=data_only)
            node = model.sections[0].body[0].body[0].body[0].next.next.body[0]
            expected = ReturnStatement(
                [Token(Token.RETURN_STATEMENT, 'RETURN', 8, 8)],
                errors=('RETURN cannot be used in FINALLY branch.',)
            )
            remove_non_data_nodes_and_assert(node, expected, data_only)


if __name__ == '__main__':
    unittest.main()
