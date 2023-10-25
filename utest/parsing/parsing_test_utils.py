import ast

from robot.parsing import ModelTransformer
from robot.parsing.model.blocks import Container
from robot.parsing.model.statements import Statement

from robot.utils.asserts import assert_equal


def assert_model(model, expected, **expected_attrs):
    if type(model) is not type(expected):
        raise AssertionError('Incompatible types:\n%s\n%s'
                             % (dump_model(model), dump_model(expected)))
    if isinstance(model, list):
        assert_equal(len(model), len(expected),
                     '%r != %r' % (model, expected), values=False)
        for m, e in zip(model, expected):
            assert_model(m, e)
    elif isinstance(model, Container):
        assert_block(model, expected, expected_attrs)
    elif isinstance(model, Statement):
        assert_statement(model, expected)
    elif model is None and expected is None:
        pass
    else:
        raise AssertionError('Incompatible children:\n%r\n%r' % (model, expected))


def dump_model(model):
    if isinstance(model, ast.AST):
        return ast.dump(model)
    elif isinstance(model, (list, tuple)):
        return [dump_model(m) for m in model]
    elif model is None:
        return 'None'
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
    assert_equal(model.type, expected.type)
    assert_equal(len(model.tokens), len(expected.tokens))
    for m, e in zip(model.tokens, expected.tokens):
        assert_equal(m, e, formatter=repr)
    assert_equal(model._fields, ())
    assert_equal(model._attributes, ('type', 'tokens', 'lineno', 'col_offset',
                                     'end_lineno', 'end_col_offset', 'errors'))
    assert_equal(model.lineno, expected.tokens[0].lineno)
    assert_equal(model.col_offset, expected.tokens[0].col_offset)
    assert_equal(model.end_lineno, expected.tokens[-1].lineno)
    assert_equal(model.end_col_offset, expected.tokens[-1].end_col_offset)
    assert_equal(model.errors, expected.errors)


def remove_non_data(model):
    RemoveNonDataTokensVisitor().visit(model)


class RemoveNonDataTokensVisitor(ModelTransformer):

    def visit_Statement(self, node):
        node.tokens = node.data_tokens
        return node

    def visit_EmptyLine(self, none):
        return None

    def visit_Comment(self, node):
        return None
