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
    Name, KeywordCall, Arguments, EmptyLine
)
from robot.utils import PY3
from robot.utils.asserts import assert_equal, assert_raises_with_msg

if PY3:
    from pathlib import Path


DATA = '''
*** Test Cases ***
Example
    Keyword    arg
    ...    argh

*** Keywords ***
Keyword
    [Arguments]    ${arg1}    ${arg2}
    Log    Got ${arg1} and ${arg}!
'''
PATH = os.path.join(os.getenv('TEMPDIR') or tempfile.gettempdir(),
                    'test_model.robot')
EXPECTED = File([
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
            TestCase(
                header=Name([
                    Token('NAME', 'Example', 3, 0),
                    Token('EOL', '\n', 3, 7)
                ]),
                body=[
                    KeywordCall([
                        Token('SEPARATOR', '    ', 4, 0),
                        Token('KEYWORD', 'Keyword', 4, 4),
                        Token('SEPARATOR', '    ', 4, 11),
                        Token('ARGUMENT', 'arg', 4, 15),
                        Token('EOL', '\n', 4, 18),
                        Token('SEPARATOR', '    ', 5, 0),
                        Token('CONTINUATION', '...', 5, 4),
                        Token('SEPARATOR', '    ', 5, 7),
                        Token('ARGUMENT', 'argh', 5, 11),
                        Token('EOL', '\n', 5, 15)
                    ]),
                    EmptyLine([
                        Token('EOL', '\n', 6, 0)
                    ])
                ]
            )
        ]
    ),
    KeywordSection(
        header=KeywordSectionHeader([
            Token('KEYWORD_HEADER', '*** Keywords ***', 7, 0),
            Token('EOL', '\n', 7, 16)
        ]),
        body=[
            Keyword(
                header=Name([
                    Token('NAME', 'Keyword', 8, 0),
                    Token('EOL', '\n', 8, 7)
                ]),
                body=[
                    Arguments([
                        Token('SEPARATOR', '    ', 9, 0),
                        Token('ARGUMENTS', '[Arguments]', 9, 4),
                        Token('SEPARATOR', '    ', 9, 15),
                        Token('ARGUMENT', '${arg1}', 9, 19),
                        Token('SEPARATOR', '    ', 9, 26),
                        Token('ARGUMENT', '${arg2}', 9, 30),
                        Token('EOL', '\n', 9, 37)
                    ]),
                    KeywordCall([
                        Token('SEPARATOR', '    ', 10, 0),
                        Token('KEYWORD', 'Log', 10, 4),
                        Token('SEPARATOR', '    ', 10, 7),
                        Token('ARGUMENT', 'Got ${arg1} and ${arg}!', 10, 11),
                        Token('EOL', '\n', 10, 34)
                    ])
                ]
            )
        ]
    )
])


def assert_model(model, expected=EXPECTED):
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


def assert_block(model, expected):
    assert_equal(model._fields, expected._fields)
    for field in expected._fields:
        model_child = getattr(model, field)
        expected_child = getattr(expected, field)
        assert_model(model_child, expected_child)


def assert_statement(model, expected):
    assert_equal(model._fields, ('type', 'tokens'))
    assert_equal(model.type, expected.type)
    assert_equal(len(model.tokens), len(expected.tokens))
    for m, e in zip(model.tokens, expected.tokens):
        assert_equal(m, e, formatter=repr)


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
        assert_model(model)

    if PY3:

        def test_from_path_as_path(self):
            model = get_model(Path(PATH))
            assert_model(model)

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
        assert_model(get_model(PATH))

    def test_save_to_different_path(self):
        model = get_model(PATH)
        different = PATH + '.robot'
        model.save(different)
        assert_model(get_model(different))

    if PY3:

        def test_save_to_original_path_as_path(self):
            model = get_model(Path(PATH))
            os.remove(PATH)
            model.save()
            assert_model(get_model(PATH))

        def test_save_to_different_path_as_path(self):
            model = get_model(PATH)
            different = PATH + '.robot'
            model.save(Path(different))
            assert_model(get_model(different))

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
                self.names = None

            def visit_TestCaseSection(self, node):
                self.names = self.test_names
                self.generic_visit(node)

            def visit_KeywordSection(self, node):
                self.names = self.kw_names
                self.generic_visit(node)

            def visit_Name(self, node):
                self.names.append(node.name)

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
                self.names = None
                self.blocks = []
                self.statements = []

            def visit_TestCaseSection(self, node):
                self.names = self.test_names
                self.visit_Block(node)

            def visit_KeywordSection(self, node):
                self.names = self.kw_names
                self.visit_Block(node)

            def visit_Name(self, node):
                self.names.append(node.name)
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
                     ['EOL', 'TESTCASE_HEADER', 'NAME', 'KEYWORD',
                      'EOL', 'KEYWORD_HEADER', 'NAME', 'ARGUMENTS', 'KEYWORD'])

    def test_ast_NodeTransformer(self):

        class Transformer(ast.NodeTransformer):

            def visit_Tags(self, node):
                return None

            def visit_TestCaseSection(self, node):
                self.generic_visit(node)
                node.body.items.append(
                    TestCase(Name([Token('NAME', 'Added'),
                                   Token('EOL', '\n')])))
                return node

            def visit_TestCase(self, node):
                self.generic_visit(node)
                return node if node.name != 'REMOVE' else None

            def visit_Name(self, node):
                name = node.get_token(Token.NAME)
                name.value = name.value.upper()
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
        expected = File([
            TestCaseSection(
                header=TestCaseSectionHeader([
                    Token('TESTCASE_HEADER', '*** Test Cases ***', 1, 0),
                    Token('EOL', '\n', 1, 18)
                ]),
                body=[
                    TestCase(Name([Token('NAME', 'EXAMPLE', 2, 0),
                                   Token('EOL', '\n', 2, 7)])),
                    TestCase(Name([Token('NAME', 'Added'),
                                   Token('EOL', '\n')]))
                ]
            )
        ])
        assert_model(model, expected)

    def test_ModelTransformer(self):

        class Transformer(ModelTransformer):

            def visit_TestCaseSectionHeader(self, node):
                return node

            def visit_Name(self, node):
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
        expected = File([
            TestCaseSection(
                header=TestCaseSectionHeader([
                    Token('TESTCASE_HEADER', '*** TEST CASES ***', 1, 0),
                    Token('EOL', '\n', 1, 18)
                ]),
                body=[
                    TestCase(Name([Token('NAME', 'EXAMPLE', 2, 0),
                                   Token('EOL', '\n', 2, 7)])),
                ]
            )
        ])
        assert_model(model, expected)


if __name__ == '__main__':
    unittest.main()
