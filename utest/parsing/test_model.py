import ast
import os
import unittest
import tempfile
from pathlib import Path

from robot.parsing import get_model, get_resource_model, ModelVisitor, ModelTransformer, Token
from robot.parsing.model.blocks import (
    File, For, If, ImplicitCommentSection, InvalidSection, Try, While,
    Keyword, KeywordSection, SettingSection, TestCase, TestCaseSection, VariableSection
)
from robot.parsing.model.statements import (
    Arguments, Break, Comment, Config, Continue, Documentation, ForHeader, End, ElseHeader,
    ElseIfHeader, EmptyLine, Error, IfHeader, InlineIfHeader, TryHeader, ExceptHeader,
    FinallyHeader, KeywordCall, KeywordName, Return, ReturnSetting, ReturnStatement,
    SectionHeader, TestCaseName, TestTags, Var, Variable, WhileHeader
)
from robot.utils.asserts import assert_equal, assert_raises_with_msg

from parsing_test_utils import assert_model, remove_non_data


DATA = '''\

*** Test Cases ***

Example
  # Comment
    Keyword    arg
    ...\targh

\t\t
*** Keywords ***
# Comment    continues
Keyword
    [Arguments]    ${arg1}    ${arg2}
    Log    Got ${arg1} and ${arg}!
    RETURN    x
'''
PATH = Path(os.getenv('TEMPDIR') or tempfile.gettempdir(), 'test_model.robot')
EXPECTED = File(sections=[
    ImplicitCommentSection(
        body=[
            EmptyLine([
                Token('EOL', '\n', 1, 0)
            ])
        ]
    ),
    TestCaseSection(
        header=SectionHeader([
            Token('TESTCASE HEADER', '*** Test Cases ***', 2, 0),
            Token('EOL', '\n', 2, 18)
        ]),
        body=[
            EmptyLine([Token('EOL', '\n', 3, 0)]),
            TestCase(
                header=TestCaseName([
                    Token('TESTCASE NAME', 'Example', 4, 0),
                    Token('EOL', '\n', 4, 7)
                ]),
                body=[
                    Comment([
                        Token('SEPARATOR', '  ', 5, 0),
                        Token('COMMENT', '# Comment', 5, 2),
                        Token('EOL', '\n', 5, 11),
                    ]),
                    KeywordCall([
                        Token('SEPARATOR', '    ', 6, 0),
                        Token('KEYWORD', 'Keyword', 6, 4),
                        Token('SEPARATOR', '    ', 6, 11),
                        Token('ARGUMENT', 'arg', 6, 15),
                        Token('EOL', '\n', 6, 18),
                        Token('SEPARATOR', '    ', 7, 0),
                        Token('CONTINUATION', '...', 7, 4),
                        Token('SEPARATOR', '\t', 7, 7),
                        Token('ARGUMENT', 'argh', 7, 8),
                        Token('EOL', '\n', 7, 12)
                    ]),
                    EmptyLine([Token('EOL', '\n', 8, 0)]),
                    EmptyLine([Token('EOL', '\t\t\n', 9, 0)])
                ]
            )
        ]
    ),
    KeywordSection(
        header=SectionHeader([
            Token('KEYWORD HEADER', '*** Keywords ***', 10, 0),
            Token('EOL', '\n', 10, 16)
        ]),
        body=[
            Comment([
                Token('COMMENT', '# Comment', 11, 0),
                Token('SEPARATOR', '    ', 11, 9),
                Token('COMMENT', 'continues', 11, 13),
                Token('EOL', '\n', 11, 22),
            ]),
            Keyword(
                header=KeywordName([
                    Token('KEYWORD NAME', 'Keyword', 12, 0),
                    Token('EOL', '\n', 12, 7)
                ]),
                body=[
                    Arguments([
                        Token('SEPARATOR', '    ', 13, 0),
                        Token('ARGUMENTS', '[Arguments]', 13, 4),
                        Token('SEPARATOR', '    ', 13, 15),
                        Token('ARGUMENT', '${arg1}', 13, 19),
                        Token('SEPARATOR', '    ', 13, 26),
                        Token('ARGUMENT', '${arg2}', 13, 30),
                        Token('EOL', '\n', 13, 37)
                    ]),
                    KeywordCall([
                        Token('SEPARATOR', '    ', 14, 0),
                        Token('KEYWORD', 'Log', 14, 4),
                        Token('SEPARATOR', '    ', 14, 7),
                        Token('ARGUMENT', 'Got ${arg1} and ${arg}!', 14, 11),
                        Token('EOL', '\n', 14, 34)
                    ]),
                    ReturnStatement([
                        Token('SEPARATOR', '    ', 15, 0),
                        Token('RETURN STATEMENT', 'RETURN', 15, 4),
                        Token('SEPARATOR', '    ', 15, 10),
                        Token('ARGUMENT', 'x', 15, 14),
                        Token('EOL', '\n', 15, 15)
                    ])
                ]
            )
        ]
    )
])


def get_and_assert_model(data, expected, depth=2):
    for data_only in True, False:
        model = get_model(data.strip(), data_only=data_only)
        if not data_only:
            remove_non_data(model)
        node = model.sections[0]
        for _ in range(depth):
            node = node.body[0]
        assert_model(node, expected)
    return node


class TestGetModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        PATH.write_text(DATA)

    @classmethod
    def tearDownClass(cls):
        PATH.unlink()

    def test_from_string(self):
        model = get_model(DATA)
        assert_model(model, EXPECTED)

    def test_from_path_as_string(self):
        model = get_model(str(PATH))
        assert_model(model, EXPECTED, source=PATH)

    def test_from_path_as_path(self):
        model = get_model(PATH)
        assert_model(model, EXPECTED, source=PATH)

    def test_from_open_file(self):
        with open(PATH) as f:
            model = get_model(f)
        assert_model(model, EXPECTED)


class TestSaveModel(unittest.TestCase):
    different_path = PATH.parent / 'different.robot'

    @classmethod
    def setUpClass(cls):
        PATH.write_text(DATA)

    @classmethod
    def tearDownClass(cls):
        PATH.unlink()
        if cls.different_path.exists:
            cls.different_path.unlink()

    def test_save_to_original_path(self):
        model = get_model(PATH)
        PATH.unlink()
        model.save()
        assert_model(get_model(PATH), EXPECTED, source=PATH)

    def test_save_to_different_path(self):
        model = get_model(PATH)
        path = self.different_path
        model.save(path)
        assert_model(get_model(path), EXPECTED, source=path)

    def test_save_to_original_path_as_str(self):
        model = get_model(str(PATH))
        PATH.unlink()
        model.save()
        assert_model(get_model(PATH), EXPECTED, source=PATH)

    def test_save_to_different_path_as_str(self):
        model = get_model(PATH)
        path = self.different_path
        model.save(Path(path))
        assert_model(get_model(path), EXPECTED, source=path)

    def test_save_to_original_fails_if_source_is_not_path(self):
        message = 'Saving model requires explicit output ' \
                  'when original source is not path.'
        assert_raises_with_msg(TypeError, message, get_model(DATA).save)
        with open(PATH) as f:
            assert_raises_with_msg(TypeError, message, get_model(f).save)


class TestForLoop(unittest.TestCase):

    def test_valid(self):
        data = '''
*** Test Cases ***
Example
    FOR    ${x}    IN    a    b    c
        Log    ${x}
    END
'''
        expected = For(
            header=ForHeader([
                Token(Token.FOR, 'FOR', 3, 4),
                Token(Token.VARIABLE, '${x}', 3, 11),
                Token(Token.FOR_SEPARATOR, 'IN', 3, 19),
                Token(Token.ARGUMENT, 'a', 3, 25),
                Token(Token.ARGUMENT, 'b', 3, 30),
                Token(Token.ARGUMENT, 'c', 3, 35),
            ]),
            body=[
                KeywordCall([Token(Token.KEYWORD, 'Log', 4, 8),
                             Token(Token.ARGUMENT, '${x}', 4, 15)])
            ],
            end=End([
                Token(Token.END, 'END', 5, 4)
            ])
        )
        get_and_assert_model(data, expected)

    def test_enumerate_with_start(self):
        data = '''
*** Test Cases ***
Example
    FOR    ${x}    IN ENUMERATE    @{stuff}    start=1
        Log    ${x}
    END
'''
        expected = For(
            header=ForHeader([
                Token(Token.FOR, 'FOR', 3, 4),
                Token(Token.VARIABLE, '${x}', 3, 11),
                Token(Token.FOR_SEPARATOR, 'IN ENUMERATE', 3, 19),
                Token(Token.ARGUMENT, '@{stuff}', 3, 35),
                Token(Token.OPTION, 'start=1', 3, 47),
            ]),
            body=[
                KeywordCall([Token(Token.KEYWORD, 'Log', 4, 8),
                             Token(Token.ARGUMENT, '${x}', 4, 15)])
            ],
            end=End([
                Token(Token.END, 'END', 5, 4)
            ])
        )
        get_and_assert_model(data, expected)

    def test_nested(self):
        data = '''
*** Test Cases ***
Example
    FOR    ${x}    IN    1    start=has no special meaning here
        FOR    ${y}    IN RANGE    ${x}
            Log    ${y}
        END
    END
'''
        expected = For(
            header=ForHeader([
                Token(Token.FOR, 'FOR', 3, 4),
                Token(Token.VARIABLE, '${x}', 3, 11),
                Token(Token.FOR_SEPARATOR, 'IN', 3, 19),
                Token(Token.ARGUMENT, '1', 3, 25),
                Token(Token.ARGUMENT, 'start=has no special meaning here', 3, 30),
            ]),
            body=[
                For(
                    header=ForHeader([
                        Token(Token.FOR, 'FOR', 4, 8),
                        Token(Token.VARIABLE, '${y}', 4, 15),
                        Token(Token.FOR_SEPARATOR, 'IN RANGE', 4, 23),
                        Token(Token.ARGUMENT, '${x}', 4, 35),
                    ]),
                    body=[
                        KeywordCall([Token(Token.KEYWORD, 'Log', 5, 12),
                                     Token(Token.ARGUMENT, '${y}', 5, 19)])
                    ],
                    end=End([
                        Token(Token.END, 'END', 6, 8)
                    ])
                )
            ],
            end=End([
                Token(Token.END, 'END', 7, 4)
            ])
        )
        get_and_assert_model(data, expected)

    def test_invalid(self):
        data1 = '''
*** Test Cases ***
Example
    FOR

    END    ooops
'''
        data2 = '''
*** Test Cases ***
Example
    FOR    wrong    IN
'''
        expected1 = For(
            header=ForHeader(
                tokens=[Token(Token.FOR, 'FOR', 3, 4)],
                errors=('FOR loop has no loop variables.',
                        "FOR loop has no 'IN' or other valid separator."),
            ),
            end=End(
                tokens=[Token(Token.END, 'END', 5, 4),
                        Token(Token.ARGUMENT, 'ooops', 5, 11)],
                errors=("END does not accept arguments, got 'ooops'.",)
            ),
            errors=('FOR loop cannot be empty.',)
        )
        expected2 = For(
            header=ForHeader(
                tokens=[Token(Token.FOR, 'FOR', 3, 4),
                        Token(Token.VARIABLE, 'wrong', 3, 11),
                        Token(Token.FOR_SEPARATOR, 'IN', 3, 20)],
                errors=("FOR loop has invalid loop variable 'wrong'.",
                        "FOR loop has no loop values."),
            ),
            errors=('FOR loop cannot be empty.',
                    'FOR loop must have closing END.')
        )
        get_and_assert_model(data1, expected1)
        get_and_assert_model(data2, expected2)


class TestWhileLoop(unittest.TestCase):

    def test_valid(self):
        data = '''
*** Test Cases ***
Example
    WHILE    True
        Log    ${x}
    END
'''
        expected = While(
            header=WhileHeader([
                Token(Token.WHILE, 'WHILE', 3, 4),
                Token(Token.ARGUMENT, 'True', 3, 13),
            ]),
            body=[
                KeywordCall([Token(Token.KEYWORD, 'Log', 4, 8),
                             Token(Token.ARGUMENT, '${x}', 4, 15)])
            ],
            end=End([
                Token(Token.END, 'END', 5, 4)
            ])
        )
        get_and_assert_model(data, expected)

    def test_limit(self):
        data = '''
*** Test Cases ***
Example
    WHILE    True    limit=100
        Log    ${x}
    END
'''
        expected = While(
            header=WhileHeader([
                Token(Token.WHILE, 'WHILE', 3, 4),
                Token(Token.ARGUMENT, 'True', 3, 13),
                Token(Token.OPTION, 'limit=100', 3, 21),
            ]),
            body=[
                KeywordCall([Token(Token.KEYWORD, 'Log', 4, 8),
                             Token(Token.ARGUMENT, '${x}', 4, 15)])
            ],
            end=End([
                Token(Token.END, 'END', 5, 4)
            ])
        )
        get_and_assert_model(data, expected)

    def test_on_limit_message(self):
        data = '''
*** Test Cases ***
Example
    WHILE    True    limit=10s    on_limit=pass    on_limit_message=Error message
        Log    ${x}
    END
'''
        expected = While(
            header=WhileHeader([
                Token(Token.WHILE, 'WHILE', 3, 4),
                Token(Token.ARGUMENT, 'True', 3, 13),
                Token(Token.OPTION, 'limit=10s', 3, 21),
                Token(Token.OPTION, 'on_limit=pass', 3, 34),
                Token(Token.OPTION, 'on_limit_message=Error message', 3, 51)
            ]),
            body=[
                KeywordCall([Token(Token.KEYWORD, 'Log', 4, 8),
                             Token(Token.ARGUMENT, '${x}', 4, 15)])
            ],
            end=End([
                Token(Token.END, 'END', 5, 4)
            ])
        )
        get_and_assert_model(data, expected)

    def test_invalid(self):
        data = '''
*** Test Cases ***
Example
    WHILE    too    many    values    !    limit=1    on_limit=bad
        # Empty body
    END
'''
        expected = While(
            header=WhileHeader(
                tokens=[Token(Token.WHILE, 'WHILE', 3, 4),
                        Token(Token.ARGUMENT, 'too', 3, 13),
                        Token(Token.ARGUMENT, 'many', 3, 20),
                        Token(Token.ARGUMENT, 'values', 3, 28),
                        Token(Token.ARGUMENT, '!', 3, 38),
                        Token(Token.OPTION, 'limit=1', 3, 43),
                        Token(Token.OPTION, 'on_limit=bad', 3, 54)],
                errors=(
                    "WHILE accepts only one condition, got 4 conditions 'too', "
                    "'many', 'values' and '!'.",
                    "WHILE option 'on_limit' does not accept value 'bad'. "
                    "Valid values are 'PASS' and 'FAIL'."
                )
            ),
            end=End([
                Token(Token.END, 'END', 5, 4)
            ]),
            errors=('WHILE loop cannot be empty.',)
        )
        get_and_assert_model(data, expected)


class TestIf(unittest.TestCase):

    def test_if(self):
        data = '''
*** Test Cases ***
Example
    IF    True
        Keyword
        Another    argument
    END
    '''
        expected = If(
            header=IfHeader([
                Token(Token.IF, 'IF', 3, 4),
                Token(Token.ARGUMENT, 'True', 3, 10),
            ]),
            body=[
                KeywordCall([Token(Token.KEYWORD, 'Keyword', 4, 8)]),
                KeywordCall([Token(Token.KEYWORD, 'Another', 5, 8),
                             Token(Token.ARGUMENT, 'argument', 5, 19)])
            ],
            end=End([Token(Token.END, 'END', 6, 4)])
        )
        get_and_assert_model(data, expected)

    def test_if_else_if_else(self):
        data = '''
*** Test Cases ***
Example
    IF    True
        K1
    ELSE IF    False
        K2
    ELSE
        K3
    END
    '''
        expected = If(
            header=IfHeader([
                Token(Token.IF, 'IF', 3, 4),
                Token(Token.ARGUMENT, 'True', 3, 10),
            ]),
            body=[
                KeywordCall([Token(Token.KEYWORD, 'K1', 4, 8)])
            ],
            orelse=If(
                header=ElseIfHeader([
                    Token(Token.ELSE_IF, 'ELSE IF', 5, 4),
                    Token(Token.ARGUMENT, 'False', 5, 15),
                ]),
                body=[
                    KeywordCall([Token(Token.KEYWORD, 'K2', 6, 8)])
                ],
                orelse=If(
                    header=ElseHeader([
                        Token(Token.ELSE, 'ELSE', 7, 4),
                    ]),
                    body=[
                        KeywordCall([Token(Token.KEYWORD, 'K3', 8, 8)])
                    ],
                )
            ),
            end=End([Token(Token.END, 'END', 9, 4)])
        )
        get_and_assert_model(data, expected)

    def test_nested(self):
        data = '''
*** Test Cases ***
Example
    IF    ${x}
        Log    ${x}
        IF    ${y}
            Log    ${y}
        ELSE
            Log    ${z}
        END
    END
'''
        expected = If(
            header=IfHeader([
                Token(Token.IF, 'IF', 3, 4),
                Token(Token.ARGUMENT, '${x}', 3, 10),
            ]),
            body=[
                KeywordCall([Token(Token.KEYWORD, 'Log', 4, 8),
                             Token(Token.ARGUMENT, '${x}', 4, 15)]),
                If(
                    header=IfHeader([
                        Token(Token.IF, 'IF', 5, 8),
                        Token(Token.ARGUMENT, '${y}', 5, 14),
                    ]),
                    body=[
                        KeywordCall([Token(Token.KEYWORD, 'Log', 6, 12),
                                     Token(Token.ARGUMENT, '${y}', 6, 19)])
                    ],
                    orelse=If(
                        header=ElseHeader([
                            Token(Token.ELSE, 'ELSE', 7, 8)
                        ]),
                        body=[
                            KeywordCall([Token(Token.KEYWORD, 'Log', 8, 12),
                                         Token(Token.ARGUMENT, '${z}', 8, 19)])
                        ]
                    ),
                    end=End([
                        Token(Token.END, 'END', 9, 8)
                    ])
                )
            ],
            end=End([
                Token(Token.END, 'END', 10, 4)
            ])
        )
        get_and_assert_model(data, expected)

    def test_invalid(self):
        data1 = '''
*** Test Cases ***
Example
    IF
    ELSE    ooops
        # Empty
    ELSE IF

    END    ooops
'''
        data2 = '''
*** Test Cases ***
Example
    IF
'''
        expected1 = If(
            header=IfHeader(
                tokens=[Token(Token.IF, 'IF', 3, 4)],
                errors=('IF must have a condition.',)
            ),
            orelse=If(
                header=ElseHeader(
                    tokens=[Token(Token.ELSE, 'ELSE', 4, 4),
                            Token(Token.ARGUMENT, 'ooops', 4, 12)],
                    errors=("ELSE does not accept arguments, got 'ooops'.",)
                ),
                orelse=If(
                    header=ElseIfHeader(
                        tokens=[Token(Token.ELSE_IF, 'ELSE IF', 6, 4)],
                        errors=('ELSE IF must have a condition.',)
                    ),
                    errors=('ELSE IF branch cannot be empty.',)
                ),
                errors=('ELSE branch cannot be empty.',)
            ),
            end=End(
                tokens=[Token(Token.END, 'END', 8, 4),
                        Token(Token.ARGUMENT, 'ooops', 8, 11)],
                errors=("END does not accept arguments, got 'ooops'.",)
            ),
            errors=('IF branch cannot be empty.',
                    'ELSE IF not allowed after ELSE.')
        )
        expected2 = If(
            header=IfHeader(
                tokens=[Token(Token.IF, 'IF', 3, 4)],
                errors=('IF must have a condition.',)
            ),
            errors=('IF branch cannot be empty.',
                    'IF must have closing END.')
        )
        get_and_assert_model(data1, expected1)
        get_and_assert_model(data2, expected2)


class TestInlineIf(unittest.TestCase):

    def test_if(self):
        data = '''
*** Test Cases ***
Example
    IF    True    Keyword
'''
        expected = If(
            header=InlineIfHeader([Token(Token.INLINE_IF, 'IF', 3, 4),
                                   Token(Token.ARGUMENT, 'True', 3, 10)]),
            body=[KeywordCall([Token(Token.KEYWORD, 'Keyword', 3, 18)])],
            end=End([Token(Token.END, '', 3, 25)])
        )
        get_and_assert_model(data, expected)

    def test_if_else_if_else(self):
        data = '''
*** Test Cases ***
Example
    IF    True    K1    ELSE IF    False    K2    ELSE    K3
'''
        expected = If(
            header=InlineIfHeader([Token(Token.INLINE_IF, 'IF', 3, 4),
                                   Token(Token.ARGUMENT, 'True', 3, 10)]),
            body=[KeywordCall([Token(Token.KEYWORD, 'K1', 3, 18)])],
            orelse=If(
                header=ElseIfHeader([Token(Token.ELSE_IF, 'ELSE IF', 3, 24),
                                     Token(Token.ARGUMENT, 'False', 3, 35)]),
                body=[KeywordCall([Token(Token.KEYWORD, 'K2', 3, 44)])],
                orelse=If(
                    header=ElseHeader([Token(Token.ELSE, 'ELSE', 3, 50)]),
                    body=[KeywordCall([Token(Token.KEYWORD, 'K3', 3, 58)])],
                )
            ),
            end=End([Token(Token.END, '', 3, 60)])
        )
        get_and_assert_model(data, expected)

    def test_nested(self):
        data = '''
*** Test Cases ***
Example
    IF    ${x}    IF    ${y}    K1    ELSE    IF    ${z}    K2
'''
        expected = If(
            header=InlineIfHeader([Token(Token.INLINE_IF, 'IF', 3, 4),
                                   Token(Token.ARGUMENT, '${x}', 3, 10)]),
            body=[If(
                header=InlineIfHeader([Token(Token.INLINE_IF, 'IF', 3, 18),
                                       Token(Token.ARGUMENT, '${y}', 3, 24)]),
                body=[KeywordCall([Token(Token.KEYWORD, 'K1', 3, 32)])],
                orelse=If(
                    header=ElseHeader([Token(Token.ELSE, 'ELSE', 3, 38)]),
                    body=[If(
                        header=InlineIfHeader([Token(Token.INLINE_IF, 'IF', 3, 46),
                                               Token(Token.ARGUMENT, '${z}', 3, 52)]),
                        body=[KeywordCall([Token(Token.KEYWORD, 'K2', 3, 60)])],
                        end=End([Token(Token.END, '', 3, 62)]),
                    )],
                ),
                errors=('Inline IF cannot be nested.',),
            )],
            errors=('Inline IF cannot be nested.',),
        )
        get_and_assert_model(data, expected)

    def test_assign(self):
        data = '''
*** Test Cases ***
Example
    ${x} =    IF    True    K1    ELSE    K2
'''
        expected = If(
            header=InlineIfHeader([Token(Token.ASSIGN, '${x} =', 3, 4),
                                   Token(Token.INLINE_IF, 'IF', 3, 14),
                                   Token(Token.ARGUMENT, 'True', 3, 20)]),
            body=[KeywordCall([Token(Token.KEYWORD, 'K1', 3, 28)])],
            orelse=If(
                header=ElseHeader([Token(Token.ELSE, 'ELSE', 3, 34)]),
                body=[KeywordCall([Token(Token.KEYWORD, 'K2', 3, 42)])],
            ),
            end=End([Token(Token.END, '', 3, 44)])
        )
        get_and_assert_model(data, expected)

    def test_assign_only_inside(self):
        data = '''
*** Test Cases ***
Example
    IF    ${cond}    ${assign}
'''
        expected = If(
            header=InlineIfHeader([Token(Token.INLINE_IF, 'IF', 3, 4),
                                   Token(Token.ARGUMENT, '${cond}', 3, 10)]),
            body=[KeywordCall([Token(Token.ASSIGN, '${assign}', 3, 21)])],
            end=End([Token(Token.END, '', 3, 30)]),
            errors=('Inline IF branches cannot contain assignments.',)
        )
        get_and_assert_model(data, expected)

    def test_invalid(self):
        data1 = '''
*** Test Cases ***
Example
    ${x} =    ${y}    IF    ELSE    ooops    ELSE IF
'''
        data2 = '''
*** Test Cases ***
Example
    IF    e    K    ELSE
'''
        expected1 = If(
            header=InlineIfHeader([Token(Token.ASSIGN, '${x} =', 3, 4),
                                   Token(Token.ASSIGN, '${y}', 3, 14),
                                   Token(Token.INLINE_IF, 'IF', 3, 22),
                                   Token(Token.ARGUMENT, 'ELSE', 3, 28)]),
            body=[KeywordCall([Token(Token.KEYWORD, 'ooops', 3, 36)])],
            orelse=If(
                header=ElseIfHeader([Token(Token.ELSE_IF, 'ELSE IF', 3, 45)],
                                    errors=('ELSE IF must have a condition.',)),
                errors=('ELSE IF branch cannot be empty.',),
            ),
            end=End([Token(Token.END, '', 3, 52)])
        )
        expected2 = If(
            header=InlineIfHeader([Token(Token.INLINE_IF, 'IF', 3, 4),
                                   Token(Token.ARGUMENT, 'e', 3, 10)]),
            body=[KeywordCall([Token(Token.KEYWORD, 'K', 3, 15)])],
            orelse=If(
                header=ElseHeader([Token(Token.ELSE, 'ELSE', 3, 20)]),
                errors=('ELSE branch cannot be empty.',),
            ),
            end=End([Token(Token.END, '', 3, 24)])
        )
        get_and_assert_model(data1, expected1)
        get_and_assert_model(data2, expected2)


class TestTry(unittest.TestCase):

    def test_try_except_else_finally(self):
        data = '''
*** Test Cases ***
Example
    TRY
        Fail    Oh no!
    EXCEPT    does not match
        No operation
    EXCEPT    AS    ${exp}
        Log    Catch
    ELSE
        No operation
    FINALLY
        Log    finally here!
    END
'''
        expected = Try(
            header=TryHeader([Token(Token.TRY, 'TRY', 3, 4)]),
            body=[KeywordCall([Token(Token.KEYWORD, 'Fail', 4, 8),
                               Token(Token.ARGUMENT, 'Oh no!', 4, 16)])],
            next=Try(
                header=ExceptHeader([Token(Token.EXCEPT, 'EXCEPT', 5, 4),
                                     Token(Token.ARGUMENT, 'does not match', 5, 14)]),
                body=[KeywordCall((Token(Token.KEYWORD, 'No operation', 6, 8),))],
                next=Try(
                    header=ExceptHeader([Token(Token.EXCEPT, 'EXCEPT', 7, 4),
                                         Token(Token.AS, 'AS', 7, 14),
                                         Token(Token.VARIABLE, '${exp}', 7, 20)]),
                    body=[KeywordCall([Token(Token.KEYWORD, 'Log', 8, 8),
                                       Token(Token.ARGUMENT, 'Catch', 8, 15)])],
                    next=Try(
                        header=ElseHeader([Token(Token.ELSE, 'ELSE', 9, 4)]),
                        body=[KeywordCall([Token(Token.KEYWORD, 'No operation', 10, 8)])],
                        next=Try(
                            header=FinallyHeader([Token(Token.FINALLY, 'FINALLY', 11, 4)]),
                            body=[KeywordCall([Token(Token.KEYWORD, 'Log', 12, 8),
                                               Token(Token.ARGUMENT, 'finally here!', 12, 15)])]
                        )
                    )
                )
            ),
            end=End([Token(Token.END, 'END', 13, 4)])
        )
        get_and_assert_model(data, expected)

    def test_invalid(self):
        data = '''
*** Test Cases ***
Example
    TRY             invalid
    ELSE            invalid

    FINALLY         invalid
    #
    EXCEPT    AS    invalid
    EXCEPT    AS
    EXCEPT    AS    ${too}    ${many}    ${values}
    EXCEPT    xx    type=invalid
'''
        expected = Try(
            header=TryHeader(
                tokens=[Token(Token.TRY, 'TRY', 3, 4),
                        Token(Token.ARGUMENT, 'invalid', 3, 20)],
                errors=("TRY does not accept arguments, got 'invalid'.",)
            ),
            next=Try(
                header=ElseHeader(
                    tokens=[Token(Token.ELSE, 'ELSE', 4, 4),
                            Token(Token.ARGUMENT, 'invalid', 4, 20)],
                    errors=("ELSE does not accept arguments, got 'invalid'.",)
                ),
                errors=('ELSE branch cannot be empty.',),
                next=Try(
                    header=FinallyHeader(
                        tokens=[Token(Token.FINALLY, 'FINALLY', 6, 4),
                                Token(Token.ARGUMENT, 'invalid', 6, 20)],
                        errors=("FINALLY does not accept arguments, got 'invalid'.",)
                    ),
                    errors=('FINALLY branch cannot be empty.',),
                    next=Try(
                        header=ExceptHeader(
                            tokens=[Token(Token.EXCEPT, 'EXCEPT', 8, 4),
                                    Token(Token.AS, 'AS', 8, 14),
                                    Token(Token.VARIABLE, 'invalid', 8, 20)],
                            errors=("EXCEPT AS variable 'invalid' is invalid.",)
                        ),
                        errors=('EXCEPT branch cannot be empty.',),
                        next=Try(
                            header=ExceptHeader(
                                tokens=[Token(Token.EXCEPT, 'EXCEPT', 9, 4),
                                        Token(Token.AS, 'AS', 9, 14)],
                                errors=("EXCEPT AS requires a value.",)
                            ),
                            errors=('EXCEPT branch cannot be empty.',),
                            next=Try(
                                header=ExceptHeader(
                                    tokens=[Token(Token.EXCEPT, 'EXCEPT', 10, 4),
                                            Token(Token.AS, 'AS', 10, 14),
                                            Token(Token.VARIABLE, '${too}', 10, 20),
                                            Token(Token.VARIABLE, '${many}', 10, 30),
                                            Token(Token.VARIABLE, '${values}', 10, 41)],
                                    errors=("EXCEPT AS accepts only one value.",)
                                ),
                                errors=('EXCEPT branch cannot be empty.',),
                                next=Try(
                                    header=ExceptHeader(
                                        tokens=[Token(Token.EXCEPT, 'EXCEPT', 11, 4),
                                                Token(Token.ARGUMENT, 'xx', 11, 14),
                                                Token(Token.OPTION, 'type=invalid', 11, 20)],
                                        errors=("EXCEPT option 'type' does not accept value 'invalid'. "
                                                "Valid values are 'GLOB', 'REGEXP', 'START' and 'LITERAL'.",)
                                    ),
                                    errors=('EXCEPT branch cannot be empty.',),
                                )

                            )
                        )
                    )
                ),
            ),
            errors=('TRY branch cannot be empty.',
                    'EXCEPT not allowed after ELSE.',
                    'EXCEPT not allowed after FINALLY.',
                    'EXCEPT not allowed after ELSE.',
                    'EXCEPT not allowed after FINALLY.',
                    'EXCEPT not allowed after ELSE.',
                    'EXCEPT not allowed after FINALLY.',
                    'EXCEPT not allowed after ELSE.',
                    'EXCEPT not allowed after FINALLY.',
                    'EXCEPT without patterns must be last.',
                    'Only one EXCEPT without patterns allowed.',
                    'TRY must have closing END.')
        )
        get_and_assert_model(data, expected)


class TestVariables(unittest.TestCase):

    def test_valid(self):
        data = '''
*** Variables ***
${x}      value
@{y}=     two    values
&{z} =    one=item
${x${y}}  nested name
'''
        expected = VariableSection(
            header=SectionHeader(
                tokens=[Token(Token.VARIABLE_HEADER, '*** Variables ***', 1, 0)]
            ),
            body=[
                Variable([Token(Token.VARIABLE, '${x}', 2, 0),
                         Token(Token.ARGUMENT, 'value', 2, 10)]),
                Variable([Token(Token.VARIABLE, '@{y}=', 3, 0),
                          Token(Token.ARGUMENT, 'two', 3, 10),
                          Token(Token.ARGUMENT, 'values', 3, 17)]),
                Variable([Token(Token.VARIABLE, '&{z} =', 4, 0),
                          Token(Token.ARGUMENT, 'one=item', 4, 10)]),
                Variable([Token(Token.VARIABLE, '${x${y}}', 5, 0),
                          Token(Token.ARGUMENT, 'nested name', 5, 10)]),
            ]
        )
        get_and_assert_model(data, expected, depth=0)

    def test_separator(self):
        data = '''
*** Variables ***
${x}      a    b    c    separator=-
${y}      separator=
'''
        expected = VariableSection(
            header=SectionHeader(
                tokens=[Token(Token.VARIABLE_HEADER, '*** Variables ***', 1, 0)]
            ),
            body=[
                Variable([Token(Token.VARIABLE, '${x}', 2, 0),
                          Token(Token.ARGUMENT, 'a', 2, 10),
                          Token(Token.ARGUMENT, 'b', 2, 15),
                          Token(Token.ARGUMENT, 'c', 2, 20),
                          Token(Token.OPTION, 'separator=-', 2, 25)]),
                Variable([Token(Token.VARIABLE, '${y}', 3, 0),
                          Token(Token.OPTION, 'separator=', 3, 10)]),
            ]
        )
        get_and_assert_model(data, expected, depth=0)

    def test_invalid(self):
        data = '''
*** Variables ***
Ooops     I did it again
${}       invalid
${x}==    invalid
${not     closed
          invalid
&{dict}   invalid    ${invalid}
'''
        expected = VariableSection(
            header=SectionHeader(
                tokens=[Token(Token.VARIABLE_HEADER, '*** Variables ***', 1, 0)]
            ),
            body=[
                Variable(
                    tokens=[Token(Token.VARIABLE, 'Ooops', 2, 0),
                            Token(Token.ARGUMENT, 'I did it again', 2, 10)],
                    errors=("Invalid variable name 'Ooops'.",)
                ),
                Variable(
                    tokens=[Token(Token.VARIABLE, '${}', 3, 0),
                            Token(Token.ARGUMENT, 'invalid', 3, 10)],
                    errors=("Invalid variable name '${}'.",)
                ),
                Variable(
                    tokens=[Token(Token.VARIABLE, '${x}==', 4, 0),
                            Token(Token.ARGUMENT, 'invalid', 4, 10)],
                    errors=("Invalid variable name '${x}=='.",)
                ),
                Variable(
                    tokens=[Token(Token.VARIABLE, '${not', 5, 0),
                            Token(Token.ARGUMENT, 'closed', 5, 10)],
                    errors=("Invalid variable name '${not'.",)
                ),
                Variable(
                    tokens=[Token(Token.VARIABLE, '', 6, 0),
                            Token(Token.ARGUMENT, 'invalid', 6, 10)],
                    errors=("Invalid variable name ''.",)
                ),
                Variable(
                    tokens=[Token(Token.VARIABLE, '&{dict}', 7, 0),
                            Token(Token.ARGUMENT, 'invalid', 7, 10),
                            Token(Token.ARGUMENT, '${invalid}', 7, 21)],
                    errors=("Invalid dictionary variable item 'invalid'. "
                            "Items must use 'name=value' syntax or be dictionary variables themselves.",
                            "Invalid dictionary variable item '${invalid}'. "
                            "Items must use 'name=value' syntax or be dictionary variables themselves.")
                ),
            ]
        )
        get_and_assert_model(data, expected, depth=0)


class TestVar(unittest.TestCase):

    def test_valid(self):
        data = '''
*** Test Cases ***
Test
    VAR    ${x}        value
    VAR    @{y}        two    values
    VAR    &{z}        one=item
    VAR    ${x${y}}    nested name
'''
        expected = TestCase(
            header=TestCaseName([Token(Token.TESTCASE_NAME, 'Test', 2, 0)]),
            body=[
                Var([Token(Token.VAR, 'VAR', 3, 4),
                     Token(Token.VARIABLE, '${x}', 3, 11),
                     Token(Token.ARGUMENT, 'value', 3, 23)]),
                Var([Token(Token.VAR, 'VAR', 4, 4),
                     Token(Token.VARIABLE, '@{y}', 4, 11),
                     Token(Token.ARGUMENT, 'two', 4, 23),
                     Token(Token.ARGUMENT, 'values', 4, 30)]),
                Var([Token(Token.VAR, 'VAR', 5, 4),
                     Token(Token.VARIABLE, '&{z}', 5, 11),
                     Token(Token.ARGUMENT, 'one=item', 5, 23)]),
                Var([Token(Token.VAR, 'VAR', 6, 4),
                     Token(Token.VARIABLE, '${x${y}}', 6, 11),
                     Token(Token.ARGUMENT, 'nested name', 6, 23)])
            ]
        )
        test = get_and_assert_model(data, expected, depth=1)
        assert_equal([v.name for v in test.body], ['${x}', '@{y}', '&{z}', '${x${y}}'])

    def test_equals(self):
        data = '''
*** Test Cases ***
Test
    VAR    ${x} =      value
    VAR    @{y}=       two    values
'''
        expected = TestCase(
            header=TestCaseName([Token(Token.TESTCASE_NAME, 'Test', 2, 0)]),
            body=[
                Var([Token(Token.VAR, 'VAR', 3, 4),
                     Token(Token.VARIABLE, '${x} =', 3, 11),
                     Token(Token.ARGUMENT, 'value', 3, 23)]),
                Var([Token(Token.VAR, 'VAR', 4, 4),
                     Token(Token.VARIABLE, '@{y}=', 4, 11),
                     Token(Token.ARGUMENT, 'two', 4, 23),
                     Token(Token.ARGUMENT, 'values', 4, 30)]),
            ]
        )
        test = get_and_assert_model(data, expected, depth=1)
        assert_equal([v.name for v in test.body], ['${x}', '@{y}'])

    def test_options(self):
        data = r'''
*** Test Cases ***
Test
    VAR    ${a}    a         scope=TEST
    VAR    ${b}    a    b    separator=\n    scope=${scope}
    VAR    @{c}    a    b    separator=normal item    scope=global
    VAR    &{d}    k=v       separator=normal item    scope=LoCaL
    VAR    ${e}              separator=-
'''
        expected = TestCase(
            header=TestCaseName([Token(Token.TESTCASE_NAME, 'Test', 2, 0)]),
            body=[
                Var([Token(Token.VAR, 'VAR', 3, 4),
                     Token(Token.VARIABLE, '${a}', 3, 11),
                     Token(Token.ARGUMENT, 'a', 3, 19),
                     Token(Token.OPTION, 'scope=TEST', 3, 29)]),
                Var([Token(Token.VAR, 'VAR', 4, 4),
                     Token(Token.VARIABLE, '${b}', 4, 11),
                     Token(Token.ARGUMENT, 'a', 4, 19),
                     Token(Token.ARGUMENT, 'b', 4, 24),
                     Token(Token.OPTION, r'separator=\n', 4, 29),
                     Token(Token.OPTION, 'scope=${scope}', 4, 45)]),
                Var([Token(Token.VAR, 'VAR', 5, 4),
                     Token(Token.VARIABLE, '@{c}', 5, 11),
                     Token(Token.ARGUMENT, 'a', 5, 19),
                     Token(Token.ARGUMENT, 'b', 5, 24),
                     Token(Token.ARGUMENT, 'separator=normal item', 5, 29),
                     Token(Token.OPTION, 'scope=global', 5, 54)]),
                Var([Token(Token.VAR, 'VAR', 6, 4),
                     Token(Token.VARIABLE, '&{d}', 6, 11),
                     Token(Token.ARGUMENT, 'k=v', 6, 19),
                     Token(Token.ARGUMENT, 'separator=normal item', 6, 29),
                     Token(Token.OPTION, 'scope=LoCaL', 6, 54)]),
                Var([Token(Token.VAR, 'VAR', 7, 4),
                     Token(Token.VARIABLE, '${e}', 7, 11),
                     Token(Token.OPTION, 'separator=-', 7, 29)]),
            ]
        )
        test = get_and_assert_model(data, expected, depth=1)
        assert_equal([(v.scope, v.separator) for v in test.body],
                     [('TEST', None), ('${scope}', r'\n'), ('global', None),
                      ('LoCaL', None), (None, '-')])

    def test_invalid(self):
        data = '''
*** Keywords ***
Keyword
    VAR    bad      name
    VAR    ${not    closed
    VAR    ${x}==   only one = accepted
    VAR
    VAR
    ...
    VAR    &{d}     o=k    bad
    VAR    ${x}     ok     scope=bad
'''
        expected = Keyword(
            header=KeywordName([Token(Token.KEYWORD_NAME, 'Keyword', 2, 0)]),
            body=[
                Var([Token(Token.VAR, 'VAR', 3, 4),
                     Token(Token.VARIABLE, 'bad', 3, 11),
                     Token(Token.ARGUMENT, 'name', 3, 20)],
                    ["Invalid variable name 'bad'."]),
                Var([Token(Token.VAR, 'VAR', 4, 4),
                     Token(Token.VARIABLE, '${not', 4, 11),
                     Token(Token.ARGUMENT, 'closed', 4, 20)],
                    ["Invalid variable name '${not'."]),
                Var([Token(Token.VAR, 'VAR', 5, 4),
                     Token(Token.VARIABLE, '${x}==', 5, 11),
                     Token(Token.ARGUMENT, 'only one = accepted', 5, 20)],
                    ["Invalid variable name '${x}=='."]),
                Var([Token(Token.VAR, 'VAR', 6, 4)],
                    ["Invalid variable name ''."]),
                Var([Token(Token.VAR, 'VAR', 7, 4),
                     Token(Token.VARIABLE, '', 8, 7)],
                    ["Invalid variable name ''."]),
                Var([Token(Token.VAR, 'VAR', 9, 4),
                     Token(Token.VARIABLE, '&{d}', 9, 11),
                     Token(Token.ARGUMENT, 'o=k', 9, 20),
                     Token(Token.ARGUMENT, 'bad', 9, 27)],
                    ["Invalid dictionary variable item 'bad'. Items must use "
                     "'name=value' syntax or be dictionary variables themselves."]),
                Var([Token(Token.VAR, 'VAR', 10, 4),
                     Token(Token.VARIABLE, '${x}', 10, 11),
                     Token(Token.ARGUMENT, 'ok', 10, 20),
                     Token(Token.OPTION, 'scope=bad', 10, 27)],
                    ["VAR option 'scope' does not accept value 'bad'. Valid values "
                     "are 'LOCAL', 'TEST', 'TASK', 'SUITE', 'SUITES' and 'GLOBAL'."]),
            ]
        )
        get_and_assert_model(data, expected, depth=1)


class TestTestCase(unittest.TestCase):

    def test_empty_test(self):
        data = '''
*** Test Cases ***
Empty
    [Documentation]    Settings aren't enough.
'''
        expected = TestCase(
            header=TestCaseName(
                tokens=[Token(Token.TESTCASE_NAME, 'Empty', 2, 0)]
            ),
            body=[
                Documentation(
                    tokens=[Token(Token.DOCUMENTATION, '[Documentation]', 3, 4),
                            Token(Token.ARGUMENT, "Settings aren't enough.", 3, 23)]
                ),
            ],
            errors=('Test cannot be empty.',)
        )
        get_and_assert_model(data, expected, depth=1)

    def test_empty_test_name(self):
        data = '''
*** Test Cases ***
    Keyword
'''
        expected = TestCase(
            header=TestCaseName(
                tokens=[Token(Token.TESTCASE_NAME, '', 2, 0)],
                errors=('Test name cannot be empty.',)
            ),
            body=[KeywordCall(tokens=[Token(Token.KEYWORD, 'Keyword', 2, 4)])]
        )
        get_and_assert_model(data, expected, depth=1)

    def test_invalid_task(self):
        data = '''
*** Tasks ***
    [Documentation]    Empty name and body.
'''
        expected = TestCase(
            header=TestCaseName(
                tokens=[Token(Token.TESTCASE_NAME, '', 2, 0)],
                errors=('Task name cannot be empty.',)
            ),
            body=[
                Documentation(
                    tokens=[Token(Token.DOCUMENTATION, '[Documentation]', 2, 4),
                            Token(Token.ARGUMENT, 'Empty name and body.', 2, 23)]
                ),
            ],
            errors=('Task cannot be empty.',)
        )
        get_and_assert_model(data, expected, depth=1)


class TestUserKeyword(unittest.TestCase):

    def test_invalid_arg_spec(self):
        data = '''
*** Keywords ***
Invalid
    [Arguments]    ooops    ${optional}=default    ${required}
    ...    @{too}    @{many}    &{notlast}    ${x}
    Keyword
'''
        expected = Keyword(
            header=KeywordName(
                tokens=[Token(Token.KEYWORD_NAME, 'Invalid', 2, 0)]
            ),
            body=[
                Arguments(
                    tokens=[Token(Token.ARGUMENTS, '[Arguments]', 3, 4),
                            Token(Token.ARGUMENT, 'ooops', 3, 19),
                            Token(Token.ARGUMENT, '${optional}=default', 3, 28),
                            Token(Token.ARGUMENT, '${required}', 3, 51),
                            Token(Token.ARGUMENT, '@{too}', 4, 11),
                            Token(Token.ARGUMENT, '@{many}', 4, 21),
                            Token(Token.ARGUMENT, '&{notlast}', 4, 32),
                            Token(Token.ARGUMENT, '${x}', 4, 46)],
                    errors=("Invalid argument syntax 'ooops'.",
                            'Non-default argument after default arguments.',
                            'Cannot have multiple varargs.',
                            'Only last argument can be kwargs.')
                ),
                KeywordCall(
                    tokens=[Token(Token.KEYWORD, 'Keyword', 5, 4)])
            ],
        )
        get_and_assert_model(data, expected, depth=1)

    def test_empty(self):
        data = '''
*** Keywords ***
Empty
    [Arguments]    ${ok}
'''
        expected = Keyword(
            header=KeywordName(
                tokens=[Token(Token.KEYWORD_NAME, 'Empty', 2, 0)]
            ),
            body=[
                Arguments(
                    tokens=[Token(Token.ARGUMENTS, '[Arguments]', 3, 4),
                            Token(Token.ARGUMENT, '${ok}', 3, 19)]
                ),
            ],
            errors=('User keyword cannot be empty.',)
        )
        get_and_assert_model(data, expected, depth=1)

    def test_empty_name(self):
        data = '''
*** Keywords ***
    Keyword
'''
        expected = Keyword(
            header=KeywordName(
                tokens=[Token(Token.KEYWORD_NAME, '', 2, 0)],
                errors=('User keyword name cannot be empty.',)
            ),
            body=[KeywordCall(tokens=[Token(Token.KEYWORD, 'Keyword', 2, 4)])]
        )
        get_and_assert_model(data, expected, depth=1)


class TestControlStatements(unittest.TestCase):

    def test_return(self):
        data = '''
*** Keywords ***
Name
    Return    RETURN
    RETURN    RETURN
'''
        expected = Keyword(
            header=KeywordName(
                tokens=[Token(Token.KEYWORD_NAME, 'Name', 2, 0)]
            ),
            body=[
                KeywordCall([Token(Token.KEYWORD, 'Return', 3, 4),
                             Token(Token.ARGUMENT, 'RETURN', 3, 14)]),
                ReturnStatement([Token(Token.RETURN_STATEMENT, 'RETURN', 4, 4),
                                 Token(Token.ARGUMENT, 'RETURN', 4, 14)])
            ],
        )
        get_and_assert_model(data, expected, depth=1)

    def test_break(self):
        data = '''
*** Keywords ***
Name
    WHILE    True
        Break    BREAK
        BREAK
    END
'''
        expected = While(
            header=WhileHeader([Token(Token.WHILE, 'WHILE', 3, 4),
                                Token(Token.ARGUMENT, 'True', 3, 13)]),
            body=[KeywordCall([Token(Token.KEYWORD, 'Break', 4, 8),
                               Token(Token.ARGUMENT, 'BREAK', 4, 17)]),
                  Break([Token(Token.BREAK, 'BREAK', 5, 8)])],
            end=End([Token(Token.END, 'END', 6, 4)])
        )
        get_and_assert_model(data, expected)

    def test_continue(self):
        data = '''
*** Keywords ***
Name
    FOR    ${x}    IN    @{stuff}
        Continue    CONTINUE
        CONTINUE
    END
'''
        expected = For(
            header=ForHeader([Token(Token.FOR, 'FOR', 3, 4),
                              Token(Token.VARIABLE, '${x}', 3, 11),
                              Token(Token.FOR_SEPARATOR, 'IN', 3, 19),
                              Token(Token.ARGUMENT, '@{stuff}', 3, 25)]),
            body=[KeywordCall([Token(Token.KEYWORD, 'Continue', 4, 8),
                               Token(Token.ARGUMENT, 'CONTINUE', 4, 20)]),
                  Continue([Token(Token.CONTINUE, 'CONTINUE', 5, 8)])],
            end=End([Token(Token.END, 'END', 6, 4)])
        )
        get_and_assert_model(data, expected)


class TestDocumentation(unittest.TestCase):

    def test_empty(self):
        data = '''\
*** Settings ***
Documentation
'''
        expected = Documentation(
            tokens=[Token(Token.DOCUMENTATION, 'Documentation', 2, 0),
                    Token(Token.EOL, '\n', 2, 13)]
        )
        self._verify_documentation(data, expected, '')

    def test_one_line(self):
        data = '''\
*** Settings ***
Documentation    Hello!
'''
        expected = Documentation(
            tokens=[Token(Token.DOCUMENTATION, 'Documentation', 2, 0),
                    Token(Token.SEPARATOR, '    ', 2, 13),
                    Token(Token.ARGUMENT, 'Hello!', 2, 17),
                    Token(Token.EOL, '\n', 2, 23)]
        )
        self._verify_documentation(data, expected, 'Hello!')

    def test_multi_part(self):
        data = '''\
*** Settings ***
Documentation    Hello    world
'''
        expected = Documentation(
            tokens=[Token(Token.DOCUMENTATION, 'Documentation', 2, 0),
                    Token(Token.SEPARATOR, '    ', 2, 13),
                    Token(Token.ARGUMENT, 'Hello', 2, 17),
                    Token(Token.SEPARATOR, '    ', 2, 22),
                    Token(Token.ARGUMENT, 'world', 2, 26),
                    Token(Token.EOL, '\n', 2, 31)]
        )
        self._verify_documentation(data, expected, 'Hello    world')

    def test_multi_line(self):
        data = '''\
*** Settings ***
Documentation    Documentation
...              in
...              multiple lines
'''
        expected = Documentation(
            tokens=[Token(Token.DOCUMENTATION, 'Documentation', 2, 0),
                    Token(Token.SEPARATOR, '    ', 2, 13),
                    Token(Token.ARGUMENT, 'Documentation', 2, 17),
                    Token(Token.EOL, '\n', 2, 30),
                    Token(Token.CONTINUATION, '...', 3, 0),
                    Token(Token.SEPARATOR, '              ', 3, 3),
                    Token(Token.ARGUMENT, 'in', 3, 17),
                    Token(Token.EOL, '\n', 3, 19),
                    Token(Token.CONTINUATION, '...', 4, 0),
                    Token(Token.SEPARATOR, '              ', 4, 3),
                    Token(Token.ARGUMENT, 'multiple lines', 4, 17),
                    Token(Token.EOL, '\n', 4, 31)]
        )
        self._verify_documentation(data, expected, 'Documentation\nin\nmultiple lines')

    def test_multi_line_with_empty_lines(self):
        data = '''\
*** Settings ***
Documentation    Documentation
...
...              with empty
'''
        expected = Documentation(
            tokens=[Token(Token.DOCUMENTATION, 'Documentation', 2, 0),
                    Token(Token.SEPARATOR, '    ', 2, 13),
                    Token(Token.ARGUMENT, 'Documentation', 2, 17),
                    Token(Token.EOL, '\n', 2, 30),
                    Token(Token.CONTINUATION, '...', 3, 0),
                    Token(Token.ARGUMENT, '', 3, 3),
                    Token(Token.EOL, '\n', 3, 3),
                    Token(Token.CONTINUATION, '...', 4, 0),
                    Token(Token.SEPARATOR, '              ', 4, 3),
                    Token(Token.ARGUMENT, 'with empty', 4, 17),
                    Token(Token.EOL, '\n', 4, 27)]
        )
        self._verify_documentation(data, expected, 'Documentation\n\nwith empty')

    def test_no_automatic_newline_after_literal_newline(self):
        data = '''\
*** Settings ***
Documentation    No automatic\\n
...              newline
'''
        expected = Documentation(
            tokens=[Token(Token.DOCUMENTATION, 'Documentation', 2, 0),
                    Token(Token.SEPARATOR, '    ', 2, 13),
                    Token(Token.ARGUMENT, 'No automatic\\n', 2, 17),
                    Token(Token.EOL, '\n', 2, 31),
                    Token(Token.CONTINUATION, '...', 3, 0),
                    Token(Token.SEPARATOR, '              ', 3, 3),
                    Token(Token.ARGUMENT, 'newline', 3, 17),
                    Token(Token.EOL, '\n', 3, 24)]
        )
        self._verify_documentation(data, expected, 'No automatic\\nnewline')

    def test_no_automatic_newline_after_backlash(self):
        data = '''\
*** Settings ***
Documentation    No automatic \\
...              newline\\\\\\
...              and remove\\    trailing\\\\    back\\slashes\\\\\\
'''
        expected = Documentation(
            tokens=[Token(Token.DOCUMENTATION, 'Documentation', 2, 0),
                    Token(Token.SEPARATOR, '    ', 2, 13),
                    Token(Token.ARGUMENT, 'No automatic \\', 2, 17),
                    Token(Token.EOL, '\n', 2, 31),
                    Token(Token.CONTINUATION, '...', 3, 0),
                    Token(Token.SEPARATOR, '              ', 3, 3),
                    Token(Token.ARGUMENT, 'newline\\\\\\', 3, 17),
                    Token(Token.EOL, '\n', 3, 27),
                    Token(Token.CONTINUATION, '...', 4, 0),
                    Token(Token.SEPARATOR, '              ', 4, 3),
                    Token(Token.ARGUMENT, 'and remove\\', 4, 17),
                    Token(Token.SEPARATOR, '    ', 4, 28),
                    Token(Token.ARGUMENT, 'trailing\\\\', 4, 32),
                    Token(Token.SEPARATOR, '    ', 4, 42),
                    Token(Token.ARGUMENT, 'back\\slashes\\\\\\', 4, 46),
                    Token(Token.EOL, '\n', 4, 61)]
        )
        self._verify_documentation(data, expected,
                                   'No automatic newline\\\\'
                                   'and remove    trailing\\\\    back\\slashes\\\\')

    def test_preserve_indentation(self):
        data = '''\
*** Settings ***
Documentation
...    Example:
...
...        - list with
...        - two
...          items
'''
        expected = Documentation(
            tokens=[Token(Token.DOCUMENTATION, 'Documentation', 2, 0),
                    Token(Token.EOL, '\n', 2, 13),
                    Token(Token.CONTINUATION, '...', 3, 0),
                    Token(Token.SEPARATOR, '    ', 3, 3),
                    Token(Token.ARGUMENT, 'Example:', 3, 7),
                    Token(Token.EOL, '\n', 3, 15),
                    Token(Token.CONTINUATION, '...', 4, 0),
                    Token(Token.ARGUMENT, '', 4, 3),
                    Token(Token.EOL, '\n', 4, 3),
                    Token(Token.CONTINUATION, '...', 5, 0),
                    Token(Token.SEPARATOR, '        ', 5, 3),
                    Token(Token.ARGUMENT, '- list with', 5, 11),
                    Token(Token.EOL, '\n', 5, 22),
                    Token(Token.CONTINUATION, '...', 6, 0),
                    Token(Token.SEPARATOR, '        ', 6, 3),
                    Token(Token.ARGUMENT, '- two', 6, 11),
                    Token(Token.EOL, '\n', 6, 16),
                    Token(Token.CONTINUATION, '...', 7, 0),
                    Token(Token.SEPARATOR, '          ', 7, 3),
                    Token(Token.ARGUMENT, 'items', 7, 13),
                    Token(Token.EOL, '\n', 7, 18)]
        )
        self._verify_documentation(data, expected, '''\
Example:

    - list with
    - two
      items''')

    def test_preserve_indentation_with_data_on_first_doc_row(self):
        data = '''\
*** Settings ***
Documentation    Example:
...
...      - list with
...      - two
...        items
'''
        expected = Documentation(
            tokens=[Token(Token.DOCUMENTATION, 'Documentation', 2, 0),
                    Token(Token.SEPARATOR, '    ', 2, 13),
                    Token(Token.ARGUMENT, 'Example:', 2, 17),
                    Token(Token.EOL, '\n', 2, 25),
                    Token(Token.CONTINUATION, '...', 3, 0),
                    Token(Token.ARGUMENT, '', 3, 3),
                    Token(Token.EOL, '\n', 3, 3),
                    Token(Token.CONTINUATION, '...', 4, 0),
                    Token(Token.SEPARATOR, '      ', 4, 3),
                    Token(Token.ARGUMENT, '- list with', 4, 9),
                    Token(Token.EOL, '\n', 4, 20),
                    Token(Token.CONTINUATION, '...', 5, 0),
                    Token(Token.SEPARATOR, '      ', 5, 3),
                    Token(Token.ARGUMENT, '- two', 5, 9),
                    Token(Token.EOL, '\n', 5, 14),
                    Token(Token.CONTINUATION, '...', 6, 0),
                    Token(Token.SEPARATOR, '        ', 6, 3),
                    Token(Token.ARGUMENT, 'items', 6, 11),
                    Token(Token.EOL, '\n', 6, 16)]
        )
        self._verify_documentation(data, expected, '''\
Example:

- list with
- two
  items''')

    def _verify_documentation(self, data, expected, value):
        # Model has both EOLs and line numbers.
        doc = get_model(data).sections[0].body[0]
        assert_model(doc, expected)
        assert_equal(doc.value, value)
        # Model has only line numbers, no EOLs or other non-data tokens.
        doc = get_model(data, data_only=True).sections[0].body[0]
        expected.tokens = [token for token in expected.tokens
                           if token.type not in Token.NON_DATA_TOKENS]
        assert_model(doc, expected)
        assert_equal(doc.value, value)
        # Model has only EOLS, no line numbers.
        doc = Documentation.from_params(value)
        assert_equal(doc.value, value)
        # Model has no EOLs nor line numbers. Everything is just one line.
        doc.tokens = [token for token in doc.tokens if token.type != Token.EOL]
        assert_equal(doc.value, ' '.join(value.splitlines()))


class TestError(unittest.TestCase):

    def test_get_errors_from_tokens(self):
        assert_equal(Error([Token('ERROR', error='xxx')]).errors,
                     ('xxx',))
        assert_equal(Error([Token('ERROR', error='xxx'),
                            Token('ARGUMENT'),
                            Token('ERROR', error='yyy')]).errors,
                     ('xxx', 'yyy'))
        assert_equal(Error([Token('ERROR', error=e) for e in '0123456789']).errors,
                     tuple('0123456789'))

    def test_model_error(self):
        model = get_model('''\
*** Invalid ***
*** Settings ***
Invalid
Documentation
''', data_only=True)
        inv_header = (
            "Unrecognized section header '*** Invalid ***'. Valid sections: "
            "'Settings', 'Variables', 'Test Cases', 'Tasks', 'Keywords' and 'Comments'."
        )
        inv_setting = "Non-existing setting 'Invalid'."
        expected = File([
            InvalidSection(
                header=SectionHeader(
                    [Token('INVALID HEADER', '*** Invalid ***', 1, 0, inv_header)]
                )

            ),
            SettingSection(
                header=SectionHeader([
                    Token('SETTING HEADER', '*** Settings ***', 2, 0)
                ]),
                body=[
                    Error([Token('ERROR', 'Invalid', 3, 0, inv_setting)]),
                    Documentation([Token('DOCUMENTATION', 'Documentation', 4, 0)])
                ]
            )
        ])
        assert_model(model, expected)

    def test_model_error_with_fatal_error(self):
        model = get_resource_model('''\
*** Test Cases ***
''', data_only=True)
        inv_testcases = "Resource file with 'Test Cases' section is invalid."
        expected = File([
            InvalidSection(
                header=SectionHeader(
                    [Token('INVALID HEADER', '*** Test Cases ***', 1, 0, inv_testcases)])
            )
        ])
        assert_model(model, expected)

    def test_model_error_with_error_and_fatal_error(self):
        model = get_resource_model('''\
*** Invalid ***
*** Settings ***
Invalid
Documentation
*** Test Cases ***
''', data_only=True)
        inv_header = (
            "Unrecognized section header '*** Invalid ***'. Valid sections: "
            "'Settings', 'Variables', 'Keywords' and 'Comments'."
        )
        inv_setting = "Non-existing setting 'Invalid'."
        inv_testcases = "Resource file with 'Test Cases' section is invalid."
        expected = File([
            InvalidSection(
                header=SectionHeader(
                    [Token('INVALID HEADER', '*** Invalid ***', 1, 0, inv_header)]
                )
            ),
            SettingSection(
                header=SectionHeader([
                    Token('SETTING HEADER', '*** Settings ***', 2, 0)
                ]),
                body=[
                    Error([Token('ERROR', 'Invalid', 3, 0, inv_setting)]),
                    Documentation([Token('DOCUMENTATION', 'Documentation', 4, 0)]),
                ]
            ),
            InvalidSection(
                header=SectionHeader(
                    [Token('INVALID HEADER', '*** Test Cases ***', 5, 0, inv_testcases)]
                )
            ),
        ])
        assert_model(model, expected)

    def test_set_errors_explicitly(self):
        error = Error([])
        error.errors = ('explicitly set', 'errors')
        assert_equal(error.errors, ('explicitly set', 'errors'))
        error.tokens = [Token('ERROR', error='normal error'),]
        assert_equal(error.errors, ('normal error',
                                    'explicitly set', 'errors'))
        error.errors = ['errors', 'as', 'list']
        assert_equal(error.errors, ('normal error',
                                    'errors', 'as', 'list'))


class TestModelVisitors(unittest.TestCase):

    def test_ast_NodeVisitor(self):

        class Visitor(ast.NodeVisitor):

            def __init__(self):
                self.test_names = []
                self.kw_names = []

            def visit_TestCaseName(self, node):
                self.test_names.append(node.name)

            def visit_KeywordName(self, node):
                self.kw_names.append(node.name)

            def visit_Block(self, node):
                raise RuntimeError('Should not be executed.')

            def visit_Statement(self, node):
                raise RuntimeError('Should not be executed.')

        visitor = Visitor()
        visitor.visit(get_model(DATA))
        assert_equal(visitor.test_names, ['Example'])
        assert_equal(visitor.kw_names, ['Keyword'])

    def test_ModelVisitor(self):

        class Visitor(ModelVisitor):

            def __init__(self):
                self.test_names = []
                self.kw_names = []
                self.blocks = []
                self.statements = []

            def visit_TestCaseName(self, node):
                self.test_names.append(node.name)
                self.visit_Statement(node)

            def visit_KeywordName(self, node):
                self.kw_names.append(node.name)
                self.visit_Statement(node)

            def visit_Block(self, node):
                self.blocks.append(type(node).__name__)
                self.generic_visit(node)

            def visit_Statement(self, node):
                self.statements.append(node.type)

        visitor = Visitor()
        visitor.visit(get_model(DATA))
        assert_equal(visitor.test_names, ['Example'])
        assert_equal(visitor.kw_names, ['Keyword'])
        assert_equal(visitor.blocks,
                     ['ImplicitCommentSection', 'TestCaseSection', 'TestCase',
                      'KeywordSection', 'Keyword'])
        assert_equal(visitor.statements,
                     ['EOL', 'TESTCASE HEADER', 'EOL', 'TESTCASE NAME',
                      'COMMENT', 'KEYWORD', 'EOL', 'EOL', 'KEYWORD HEADER',
                      'COMMENT', 'KEYWORD NAME', 'ARGUMENTS', 'KEYWORD',
                      'RETURN STATEMENT'])

    def test_ast_NodeTransformer(self):

        class Transformer(ast.NodeTransformer):

            def visit_Tags(self, node):
                return None

            def visit_TestCaseSection(self, node):
                self.generic_visit(node)
                node.body.append(
                    TestCase(TestCaseName([Token('TESTCASE NAME', 'Added'),
                                           Token('EOL', '\n')]))
                )
                return node

            def visit_TestCase(self, node):
                self.generic_visit(node)
                return node if node.name != 'REMOVE' else None

            def visit_TestCaseName(self, node):
                name_token = node.get_token(Token.TESTCASE_NAME)
                name_token.value = name_token.value.upper()
                return node

            def visit_Block(self, node):
                raise RuntimeError('Should not be executed.')

            def visit_Statement(self, node):
                raise RuntimeError('Should not be executed.')

        model = get_model('''\
*** Test Cases ***
Example
    [Tags]    to be removed
Remove
''')
        Transformer().visit(model)
        expected = File(sections=[
            TestCaseSection(
                header=SectionHeader([
                    Token('TESTCASE HEADER', '*** Test Cases ***', 1, 0),
                    Token('EOL', '\n', 1, 18)
                ]),
                body=[
                    TestCase(TestCaseName([
                        Token('TESTCASE NAME', 'EXAMPLE', 2, 0),
                        Token('EOL', '\n', 2, 7)
                    ]), errors= ('Test cannot be empty.',)),
                    TestCase(TestCaseName([
                        Token('TESTCASE NAME', 'Added'),
                        Token('EOL', '\n')
                    ]))
                ]
            )
        ])
        assert_model(model, expected)

    def test_ModelTransformer(self):

        class Transformer(ModelTransformer):

            def visit_SectionHeader(self, node):
                return node

            def visit_TestCaseName(self, node):
                return node

            def visit_Statement(self, node):
                return None

            def visit_Block(self, node):
                self.generic_visit(node)
                if hasattr(node, 'header'):
                    for token in node.header.data_tokens:
                        token.value = token.value.upper()
                return node

        model = get_model('''\
*** Test Cases ***
Example
    [Tags]    to be removed
    To be removed
''')
        Transformer().visit(model)
        expected = File(sections=[
            TestCaseSection(
                header=SectionHeader([
                    Token('TESTCASE HEADER', '*** TEST CASES ***', 1, 0),
                    Token('EOL', '\n', 1, 18)
                ]),
                body=[
                    TestCase(TestCaseName([
                        Token('TESTCASE NAME', 'EXAMPLE', 2, 0),
                        Token('EOL', '\n', 2, 7)
                    ])),
                ]
            )
        ])
        assert_model(model, expected)

    def test_visit_Return(self):
        class VisitReturn(ModelVisitor):
            def visit_Return(self, node):
                self.node = node

        class VisitReturnStatement(ModelVisitor):
            def visit_ReturnStatement(self, node):
                self.node = node

        for node in Return.from_params(), ReturnStatement.from_params():
            for visitor in VisitReturn(), VisitReturnStatement():
                visitor.visit(node)
                assert_equal(visitor.node, node)

    def test_visit_ReturnSetting(self):
        class VisitReturnSetting(ModelVisitor):
            def visit_ReturnSetting(self, node):
                self.node = node

        node = ReturnSetting.from_params(())
        visitor = VisitReturnSetting()
        visitor.visit(node)
        assert_equal(visitor.node, node)

    def test_visit_ForceTags(self):
        class VisitForceTags(ModelVisitor):
            def visit_ForceTags(self, node):
                self.node = node

        node = TestTags.from_params(['t1', 't2'])
        visitor = VisitForceTags()
        visitor.visit(node)
        assert_equal(visitor.node, node)


class TestLanguageConfig(unittest.TestCase):

    def test_config(self):
        model = get_model('''\
language: fi
language: bad
language: bad    but ignored
language: de     # ok
*** Einstellungen ***
Dokumentaatio    Header is de and setting is fi.
''')
        expected = File(
            languages=('fi', 'de'),
            sections=[
                ImplicitCommentSection(body=[
                    Config([
                        Token('CONFIG', 'language: fi', 1, 0),
                        Token('EOL', '\n', 1, 12)
                    ]),
                    Error([
                        Token('ERROR', 'language: bad', 2, 0,
                              "Invalid language configuration: Language 'bad' "
                              "not found nor importable as a language module."),
                        Token('EOL', '\n', 2, 13)
                    ]),
                    Comment([
                        Token('COMMENT', 'language: bad', 3, 0),
                        Token('SEPARATOR', '    ', 3, 13),
                        Token('COMMENT', 'but ignored', 3, 17),
                        Token('EOL', '\n', 3, 28)
                    ]),
                    Config([
                        Token('CONFIG', 'language: de', 4, 0),
                        Token('SEPARATOR', '     ', 4, 12),
                        Token('COMMENT', '# ok', 4, 17),
                        Token('EOL', '\n', 4, 21)
                    ]),
                ]),
                SettingSection(
                    header=SectionHeader([
                        Token('SETTING HEADER', '*** Einstellungen ***', 5, 0),
                        Token('EOL', '\n', 5, 21)
                    ]),
                    body=[
                        Documentation([
                            Token('DOCUMENTATION', 'Dokumentaatio', 6, 0),
                            Token('SEPARATOR', '    ', 6, 13),
                            Token('ARGUMENT', 'Header is de and setting is fi.', 6, 17),
                            Token('EOL', '\n', 6, 48)
                        ])
                    ]
                )
            ]
        )
        assert_model(model, expected)


if __name__ == '__main__':
    unittest.main()
