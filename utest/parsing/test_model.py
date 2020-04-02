import ast
import os
import unittest
import tempfile

from robot.parsing import get_model, ModelVisitor, ModelTransformer, Token
from robot.parsing.model.blocks import (
    Block, File, CommentSection, TestCaseSection, KeywordSection,
    TestCase, Keyword
)
from robot.parsing.model.statements import (
    Statement, TestCaseSectionHeader, KeywordSectionHeader,
    TestCaseName, KeywordName, KeywordCall, Arguments, EmptyLine, Comment
)
from robot.utils import PY3
from robot.utils.asserts import assert_equal, assert_raises_with_msg

if PY3:
    from pathlib import Path


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
        header=TestCaseSectionHeader([
            Token('TESTCASE_HEADER', '*** Test Cases ***', 2, 0),
            Token('EOL', '\n', 2, 18)
        ]),
        body=[
            EmptyLine([Token('EOL', '\n', 3, 0)]),
            TestCase(
                header=TestCaseName([
                    Token('TESTCASE_NAME', 'Example', 4, 0),
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
        header=KeywordSectionHeader([
            Token('KEYWORD_HEADER', '*** Keywords ***', 10, 0),
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
                    Token('KEYWORD_NAME', 'Keyword', 12, 0),
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


def assert_model(model, expected=EXPECTED, source=None):
    if type(model) is not type(expected):
        raise AssertionError('Incompatible types:\n%s\n%s'
                             % (ast.dump(model), ast.dump(expected)))
    if isinstance(model, list):
        assert_equal(len(model), len(expected),
                     '%r != %r' % (model, expected), values=False)
        for m, e in zip(model, expected):
            assert_model(m, e)
    elif isinstance(model, Block):
        assert_block(model, expected)
    elif isinstance(model, Statement):
        assert_statement(model, expected)
    elif model is None and expected is None:
        pass
    else:
        raise AssertionError('Incompatible children:\n%r\n%r'
                             % (model, expected))
    if isinstance(model, File):
        assert_equal(model.source, source)


def assert_block(model, expected):
    assert_equal(model._fields, expected._fields)
    for field in expected._fields:
        assert_model(getattr(model, field), getattr(expected, field))
    assert_equal(model.lineno, expected.lineno)
    assert_equal(model.col_offset, expected.col_offset)
    assert_equal(model.end_lineno, expected.end_lineno)
    assert_equal(model.end_col_offset, expected.end_col_offset)


def assert_statement(model, expected):
    assert_equal(model._fields, ('type', 'tokens'))
    assert_equal(model.type, expected.type)
    assert_equal(len(model.tokens), len(expected.tokens))
    for m, e in zip(model.tokens, expected.tokens):
        assert_equal(m, e, formatter=repr)
    assert_equal(model._attributes, ('lineno', 'col_offset',
                                     'end_lineno', 'end_col_offset'))
    assert_equal(model.lineno, model.tokens[0].lineno)
    assert_equal(model.col_offset, model.tokens[0].col_offset)
    assert_equal(model.end_lineno, model.tokens[-1].lineno)
    assert_equal(model.end_col_offset, model.tokens[-1].end_col_offset)


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

    if PY3:

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

    if PY3:

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


class TestModelVisitors(unittest.TestCase):

    def test_ast_NodevVisitor(self):

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
                     ['File', 'CommentSection', 'Body',
                      'TestCaseSection', 'Body', 'TestCase', 'Body',
                      'KeywordSection', 'Body', 'Keyword', 'Body'])
        assert_equal(visitor.statements,
                     ['EOL', 'TESTCASE_HEADER', 'EOL', 'TESTCASE_NAME',
                      'COMMENT', 'KEYWORD', 'EOL', 'EOL', 'KEYWORD_HEADER',
                      'COMMENT', 'KEYWORD_NAME', 'ARGUMENTS', 'KEYWORD'])

    def test_ast_NodeTransformer(self):

        class Transformer(ast.NodeTransformer):

            def visit_Tags(self, node):
                return None

            def visit_TestCaseSection(self, node):
                self.generic_visit(node)
                node.body.items.append(
                    TestCase(TestCaseName([Token('TESTCASE_NAME', 'Added'),
                                           Token('EOL', '\n')])))
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
                header=TestCaseSectionHeader([
                    Token('TESTCASE_HEADER', '*** Test Cases ***', 1, 0),
                    Token('EOL', '\n', 1, 18)
                ]),
                body=[
                    TestCase(TestCaseName([
                        Token('TESTCASE_NAME', 'EXAMPLE', 2, 0),
                        Token('EOL', '\n', 2, 7)
                    ])),
                    TestCase(TestCaseName([
                        Token('TESTCASE_NAME', 'Added'),
                        Token('EOL', '\n')
                    ]))
                ]
            )
        ])
        assert_model(model, expected)

    def test_ModelTransformer(self):

        class Transformer(ModelTransformer):

            def visit_TestCaseSectionHeader(self, node):
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
                header=TestCaseSectionHeader([
                    Token('TESTCASE_HEADER', '*** TEST CASES ***', 1, 0),
                    Token('EOL', '\n', 1, 18)
                ]),
                body=[
                    TestCase(TestCaseName([
                        Token('TESTCASE_NAME', 'EXAMPLE', 2, 0),
                        Token('EOL', '\n', 2, 7)
                    ])),
                ]
            )
        ])
        assert_model(model, expected)


if __name__ == '__main__':
    unittest.main()
