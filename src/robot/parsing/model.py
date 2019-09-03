import ast

from .lexer import TestCaseFileLexer, Token
from .lexerwrapper import LexerWrapper


header_types = (
    Token.SETTING_HEADER, Token.VARIABLE_HEADER,
    Token.TESTCASE_HEADER, Token.KEYWORD_HEADER
)


class Node(ast.AST):
    _fields = ()


class File(Node):
    _fields = ('sections',)

    def __init__(self):
        self.sections = []


class Section(Node):
    _fields = ('header', 'body')

    def __init__(self, header=None, body=None):
        self.header = header
        self.body = Body(body)
        self.type = header.type if header else Token.COMMENT_HEADER


class Body(Node):
    _fields = ('items',)

    def __init__(self, items=None):
        self.items = items or []

    def add(self, item):
        self.items.append(item)


class Statement(Node):
    _fields = ('type', 'tokens')

    def __init__(self, tokens):
        self.type = self._get_type(tokens)
        self.tokens = tokens

    def _get_type(self, tokens):
        for t in tokens:
            if t.type not in (Token.SEPARATOR, Token.EOL, Token.OLD_FOR_INDENT):
                return t.type
        return None

    @property
    def lines(self):
        if self.type in Token.SETTING_TOKENS and len(self.tokens) == 1:
            return []
        line = []
        for token in self.tokens:
            if token.type != Token.CONTINUATION:
                line.append(token)
            else:
                yield line
                line = [token]
        if line:
            yield line

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, item):
        return self.tokens[item]


# TODO: maybe split into TestCase and Keyword for better AST
class TestOrKeyword(Node):
    _fields = ('name', 'body')

    def __init__(self, name_tokens):
        self.name = name_tokens
        self.body = Body()


class ForLoop(Node):
    _fields = ('type', 'header', 'body', 'end')

    def __init__(self, header_tokens):
        self.type = header_tokens.type
        self.header = header_tokens
        self.body = Body()
        self.end = None


class Builder(object):

    def __init__(self, model):
        self.model = model

    def handles(self, statement):
        return True

    def statement(self, statement):
        raise NotImplementedError


class FileBuilder(Builder):

    def statement(self, statement):
        try:
            section = Section(header=statement)
            builder_class = {
                Token.SETTING_HEADER: SectionBuilder,
                Token.VARIABLE_HEADER: SectionBuilder,
                Token.TESTCASE_HEADER: TestOrKeywordSectionBuilder,
                Token.KEYWORD_HEADER: TestOrKeywordSectionBuilder,
                Token.COMMENT_HEADER: SectionBuilder
            }[statement.type]
        except KeyError:
            section = Section(body=[statement])
            builder_class = SectionBuilder
        self.model.sections.append(section)
        return builder_class(section)


class SectionBuilder(Builder):

    def handles(self, statement):
        return statement.type not in header_types

    def statement(self, statement):
        self.model.body.add(statement)


class TestOrKeywordSectionBuilder(SectionBuilder):

    def statement(self, statement):
        model = TestOrKeyword(statement)
        self.model.body.add(model)
        return TestOrKeywordBuilder(model)


class TestOrKeywordBuilder(Builder):

    def handles(self, statement):
        return statement.type not in header_types + (Token.NAME,)

    def statement(self, statement):
        if statement.type == Token.FOR:
            model = ForLoop(statement)
            self.model.body.add(model)
            return ForLoopBuilder(model)
        else:
            self.model.body.add(statement)


class ForLoopBuilder(Builder):

    def __init__(self, model):
        Builder.__init__(self, model)
        self._end = False

    def handles(self, statement):
        return not self._end

    def statement(self, statement):
        if statement.type == Token.END:
            self.model.end = statement
            self._end = True
        else:
            self.model.body.add(statement)


def Model(source):
    builder = FileBuilder(File())
    stack = [builder]
    for statement in get_statements(source):
        while not stack[-1].handles(statement):
            stack.pop()
        builder = stack[-1].statement(statement)
        if builder:
            stack.append(builder)

    return stack[0].model


def get_statements(source):
    tokens = LexerWrapper(TestCaseFileLexer(data_only=False), source).tokens
    statement = []
    for t in tokens:
        if t.type != t.EOS:
            statement.append(t)
        else:
            yield Statement(statement)
            statement = []


if __name__ == '__main__':
    import sys
    a = Model(sys.argv[1])
    print(ast.dump(a))
