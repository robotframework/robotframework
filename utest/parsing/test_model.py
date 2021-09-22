import ast
import os
import unittest
import tempfile
from pathlib import Path

from robot.parsing import get_model, get_resource_model, ModelVisitor, ModelTransformer, Token
from robot.parsing.model.blocks import (
    Block, CommentSection, File, For, If, Keyword, KeywordSection,
    SettingSection, TestCase, TestCaseSection, VariableSection
)
from robot.parsing.model.statements import (
    Arguments, Comment, Documentation, ForHeader, End, ElseHeader, ElseIfHeader,
    EmptyLine, Error, IfHeader, KeywordCall, KeywordName, SectionHeader,
    Statement, TestCaseName, Variable
)
from robot.utils.asserts import assert_equal, assert_raises_with_msg


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
'''
PATH = os.path.join(os.getenv('TEMPDIR') or tempfile.gettempdir(),
                    'test_model.robot')
EXPECTED = File(sections=[
    CommentSection(
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
                    ])
                ]
            )
        ]
    )
])


def assert_model(model, expected=EXPECTED, **expected_attrs):
    if type(model) is not type(expected):
        raise AssertionError('Incompatible types:\n%s\n%s'
                             % (dump_model(model), dump_model(expected)))
    if isinstance(model, list):
        assert_equal(len(model), len(expected),
                     '%r != %r' % (model, expected), values=False)
        for m, e in zip(model, expected):
            assert_model(m, e)
    elif isinstance(model, Block):
        assert_block(model, expected, expected_attrs)
    elif isinstance(model, Statement):
        assert_statement(model, expected)
    elif model is None and expected is None:
        pass
    else:
        raise AssertionError('Incompatible children:\n%r\n%r'
                             % (model, expected))


def dump_model(model):
    if isinstance(model, ast.AST):
        return ast.dump(model)
    elif isinstance(model, (list, tuple)):
        return [dump_model(m) for m in model]
    else:
        raise TypeError('Invalid model %r' % model)

def assert_block(model, expected, expected_attrs):
    assert_equal(model._fields, expected._fields)
    for field in expected._fields:
        assert_model(getattr(model, field), getattr(expected, field))
    for attr in expected._attributes:
        exp = expected_attrs.get(attr, getattr(expected, attr))
        assert_equal(getattr(model, attr), exp)


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


class TestGetModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(PATH, 'w') as f:
            f.write(DATA)

    @classmethod
    def tearDownClass(cls):
        os.remove(PATH)

    def test_from_string(self):
        model = get_model(DATA)
        assert_model(model)

    def test_from_path_as_string(self):
        model = get_model(PATH)
        assert_model(model, source=PATH)

    def test_from_path_as_path(self):
        model = get_model(Path(PATH))
        assert_model(model, source=PATH)

    def test_from_open_file(self):
        with open(PATH) as f:
            model = get_model(f)
        assert_model(model)


class TestSaveModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(PATH, 'w') as f:
            f.write(DATA)

    @classmethod
    def tearDownClass(cls):
        os.remove(PATH)

    def test_save_to_original_path(self):
        model = get_model(PATH)
        os.remove(PATH)
        model.save()
        assert_model(get_model(PATH), source=PATH)

    def test_save_to_different_path(self):
        model = get_model(PATH)
        different = PATH + '.robot'
        model.save(different)
        assert_model(get_model(different), source=different)

    def test_save_to_original_path_as_path(self):
        model = get_model(Path(PATH))
        os.remove(PATH)
        model.save()
        assert_model(get_model(PATH), source=PATH)

    def test_save_to_different_path_as_path(self):
        model = get_model(PATH)
        different = PATH + '.robot'
        model.save(Path(different))
        assert_model(get_model(different), source=different)

    def test_save_to_original_fails_if_source_is_not_path(self):
        message = 'Saving model requires explicit output ' \
                  'when original source is not path.'
        assert_raises_with_msg(TypeError, message, get_model(DATA).save)
        with open(PATH) as f:
            assert_raises_with_msg(TypeError, message, get_model(f).save)


class TestForLoop(unittest.TestCase):

    def test_valid(self):
        model = get_model('''\
*** Test Cases ***
Example
    FOR    ${x}    IN    a    b    c
        Log    ${x}
    END
''', data_only=True)
        loop = model.sections[0].body[0].body[0]
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
        assert_model(loop, expected)

    def test_nested(self):
        model = get_model('''\
*** Test Cases ***
Example
    FOR    ${x}    IN    1    2
        FOR    ${y}    IN RANGE    ${x}
            Log    ${y}
        END
    END
''', data_only=True)
        loop = model.sections[0].body[0].body[0]
        expected = For(
            header=ForHeader([
                Token(Token.FOR, 'FOR', 3, 4),
                Token(Token.VARIABLE, '${x}', 3, 11),
                Token(Token.FOR_SEPARATOR, 'IN', 3, 19),
                Token(Token.ARGUMENT, '1', 3, 25),
                Token(Token.ARGUMENT, '2', 3, 30),
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
        assert_model(loop, expected)

    def test_invalid(self):
        model = get_model('''\
*** Test Cases ***
Example
    FOR
    END    ooops

    FOR    wrong    IN
''', data_only=True)
        loop1, loop2 = model.sections[0].body[0].body
        expected1 = For(
            header=ForHeader(
                tokens=[Token(Token.FOR, 'FOR', 3, 4)],
                errors=('FOR loop has no loop variables.',
                        "FOR loop has no 'IN' or other valid separator."),
            ),
            end=End(
                tokens=[Token(Token.END, 'END', 4, 4),
                        Token(Token.ARGUMENT, 'ooops', 4, 11)],
                errors=('END does not accept arguments.',)
            ),
            errors=('FOR loop has empty body.',)
        )
        expected2 = For(
            header=ForHeader(
                tokens=[Token(Token.FOR, 'FOR', 6, 4),
                        Token(Token.VARIABLE, 'wrong', 6, 11),
                        Token(Token.FOR_SEPARATOR, 'IN', 6, 20)],
                errors=("FOR loop has invalid loop variable 'wrong'.",
                        "FOR loop has no loop values."),
            ),
            errors=('FOR loop has empty body.',
                    'FOR loop has no closing END.')
        )
        assert_model(loop1, expected1)
        assert_model(loop2, expected2)


class TestIf(unittest.TestCase):

    def test_if(self):
        model = get_model('''\
*** Test Cases ***
Example
    IF    True
        Keyword
        Another    argument
    END
    ''', data_only=True)
        node = model.sections[0].body[0].body[0]
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
        assert_model(node, expected)

    def test_if_else_if_else(self):
        model = get_model('''\
*** Test Cases ***
Example
    IF    True
        K1
    ELSE IF    False
        K2
    ELSE
        K3
    END
    ''', data_only=True)
        node = model.sections[0].body[0].body[0]
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
        assert_model(node, expected)

    def test_nested(self):
        model = get_model('''\
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
''', data_only=True)
        node = model.sections[0].body[0].body[0]
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
        assert_model(node, expected)

    def test_invalid(self):
        model = get_model('''\
*** Test Cases ***
Example
    IF    too    many
    ELSE    ooops
    ELSE IF
    END    ooops

    IF
''', data_only=True)
        if1, if2 = model.sections[0].body[0].body
        expected1 = If(
            header=IfHeader(
                tokens=[Token(Token.IF, 'IF', 3, 4),
                        Token(Token.ARGUMENT, 'too', 3, 10),
                        Token(Token.ARGUMENT, 'many', 3, 17)],
                errors=('IF has more than one condition.',)
            ),
            orelse=If(
                header=ElseHeader(
                    tokens=[Token(Token.ELSE, 'ELSE', 4, 4),
                            Token(Token.ARGUMENT, 'ooops', 4, 12)],
                    errors=('ELSE has condition.',)
                ),
                orelse=If(
                    header=ElseIfHeader(
                        tokens=[Token(Token.ELSE_IF, 'ELSE IF', 5, 4)],
                        errors=('ELSE IF has no condition.',)
                    ),
                    errors=('ELSE IF has empty body.',)
                ),
                errors=('ELSE has empty body.',)
            ),
            end=End(
                tokens=[Token(Token.END, 'END', 6, 4),
                        Token(Token.ARGUMENT, 'ooops', 6, 11)],
                errors=('END does not accept arguments.',)
            ),
            errors=('IF has empty body.',
                    'ELSE IF after ELSE.')
        )
        expected2 = If(
            header=IfHeader(
                tokens=[Token(Token.IF, 'IF', 8, 4)],
                errors=('IF has no condition.',)
            ),
            errors=('IF has empty body.',
                    'IF has no closing END.')
        )
        assert_model(if1, expected1)
        assert_model(if2, expected2)


class TestVariables(unittest.TestCase):

    def test_valid(self):
        model = get_model('''\
*** Variables ***
${x}      value
@{y}=     two    values
&{z} =    one=item
''', data_only=True)
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
            ]
        )
        assert_model(model.sections[0], expected)

    def test_invalid(self):
        model = get_model('''\
*** Variables ***
Ooops     I did it again
${}       invalid
${x}==    invalid
${not     closed
          invalid
&{dict}   invalid    ${invalid}
''', data_only=True)
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
                    errors = ("Invalid variable name '${x}=='.",)
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
        assert_model(model.sections[0], expected)


class TestKeyword(unittest.TestCase):

    def test_invalid_arg_spec(self):
        model = get_model('''\
*** Keywords ***
Invalid
    [Arguments]    ooops    ${optional}=default    ${required}
    ...    @{too}    @{many}    &{notlast}    ${x}
''', data_only=True)
        expected = KeywordSection(
            header=SectionHeader(
                tokens=[Token(Token.KEYWORD_HEADER, '*** Keywords ***', 1, 0)]
            ),
            body=[
                Keyword(
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
                        )
                    ],
                )
            ]
        )
        assert_model(model.sections[0], expected)

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

    def test_get_fatal_errors_from_tokens(self):
        assert_equal(Error([Token('FATAL ERROR', error='xxx')]).errors,
                     ('xxx',))
        assert_equal(Error([Token('FATAL ERROR', error='xxx'),
                            Token('ARGUMENT'),
                            Token('FATAL ERROR', error='yyy')]).errors,
                     ('xxx', 'yyy'))
        assert_equal(Error([Token('FATAL ERROR', error=e) for e in '0123456789']).errors,
                     tuple('0123456789'))

    def test_get_errors_and_fatal_errors_from_tokens(self):
        assert_equal(Error([Token('ERROR', error='error'),
                            Token('ARGUMENT'),
                            Token('FATAL ERROR', error='fatal error')]).errors,
                     ('error', 'fatal error'))
        assert_equal(Error([Token('FATAL ERROR', error=e) for e in '0123456789']).errors,
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
            CommentSection(
                body=[
                    Error([Token('ERROR', '*** Invalid ***', 1, 0, inv_header)])
                ]
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
            CommentSection(
                body=[
                    Error([Token('FATAL ERROR', '*** Test Cases ***', 1, 0, inv_testcases)])
                ]
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
            CommentSection(
                body=[
                    Error([Token('ERROR', '*** Invalid ***', 1, 0, inv_header)])
                ]
            ),
            SettingSection(
                header=SectionHeader([
                    Token('SETTING HEADER', '*** Settings ***', 2, 0)
                ]),
                body=[
                    Error([Token('ERROR', 'Invalid', 3, 0, inv_setting)]),
                    Documentation([Token('DOCUMENTATION', 'Documentation', 4, 0)]),
                    Error([Token('FATAL ERROR', '*** Test Cases ***', 5, 0, inv_testcases)])
                ]
            )
        ])
        assert_model(model, expected)

    def test_set_errors_explicitly(self):
        error = Error([])
        error.errors = ('explicitly set', 'errors')
        assert_equal(error.errors, ('explicitly set', 'errors'))
        error.tokens = [Token('ERROR', error='normal error'),
                        Token('FATAL ERROR', error='fatal error')]
        assert_equal(error.errors, ('normal error', 'fatal error',
                                    'explicitly set', 'errors'))
        error.errors = ['errors', 'as', 'list']
        assert_equal(error.errors, ('normal error', 'fatal error',
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
                     ['File', 'CommentSection', 'TestCaseSection', 'TestCase',
                      'KeywordSection', 'Keyword'])
        assert_equal(visitor.statements,
                     ['EOL', 'TESTCASE HEADER', 'EOL', 'TESTCASE NAME',
                      'COMMENT', 'KEYWORD', 'EOL', 'EOL', 'KEYWORD HEADER',
                      'COMMENT', 'KEYWORD NAME', 'ARGUMENTS', 'KEYWORD'])

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
                    ])),
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


if __name__ == '__main__':
    unittest.main()
