#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import ast
from contextlib import contextmanager

from robot.utils import file_writer, is_pathlike, is_string

from .statements import (Break, Continue, Error, KeywordCall, ReturnSetting,
                         ReturnStatement, Statement, TemplateArguments)
from .visitor import ModelVisitor
from ..lexer import Token


class Block(ast.AST):
    _fields = ()
    _attributes = ('lineno', 'col_offset', 'end_lineno', 'end_col_offset', 'errors')
    errors = ()

    @property
    def lineno(self):
        statement = FirstStatementFinder.find_from(self)
        return statement.lineno if statement else -1

    @property
    def col_offset(self):
        statement = FirstStatementFinder.find_from(self)
        return statement.col_offset if statement else -1

    @property
    def end_lineno(self):
        statement = LastStatementFinder.find_from(self)
        return statement.end_lineno if statement else -1

    @property
    def end_col_offset(self):
        statement = LastStatementFinder.find_from(self)
        return statement.end_col_offset if statement else -1

    def validate_model(self):
        ModelValidator().visit(self)

    def validate(self, ctx: 'ValidationContext'):
        pass


class HeaderAndBody(Block):
    _fields = ('header', 'body')

    def __init__(self, header=None, body=None, errors=()):
        self.header = header
        self.body = body or []
        self.errors = errors

    def _body_is_empty(self):
        # This works with tests, keywords and blocks inside them, not with sections.
        valid = (KeywordCall, TemplateArguments, Continue, ReturnStatement, Break,
                 Block, Error)
        return not any(isinstance(node, valid) for node in self.body)


class File(Block):
    _fields = ('sections',)
    _attributes = ('source', 'languages') + Block._attributes

    def __init__(self, sections=None, source=None, languages=()):
        self.sections = sections or []
        self.source = source
        self.languages = languages

    def save(self, output=None):
        """Save model to the given ``output`` or to the original source file.

        The ``output`` can be a path to a file or an already opened file
        object. If ``output`` is not given, the original source file will
        be overwritten.
        """
        output = output or self.source
        if output is None:
            raise TypeError('Saving model requires explicit output '
                            'when original source is not path.')
        ModelWriter(output).write(self)


class Section(HeaderAndBody):
    pass


class SettingSection(Section):
    pass


class VariableSection(Section):
    pass


# TODO: should there be a separate TaskSection?
class TestCaseSection(Section):

    @property
    def tasks(self):
        return self.header.type == Token.TASK_HEADER


class KeywordSection(Section):
    pass


class CommentSection(Section):
    pass


class InvalidSection(Section):
    pass


class TestCase(HeaderAndBody):

    @property
    def name(self):
        return self.header.name

    def validate(self, ctx: 'ValidationContext'):
        if self._body_is_empty():
            # FIXME: Tasks!
            self.errors += ('Test contains no keywords.',)


class Keyword(HeaderAndBody):

    @property
    def name(self):
        return self.header.name

    def validate(self, ctx: 'ValidationContext'):
        if self._body_is_empty():
            if not any(isinstance(node, ReturnSetting) for node in self.body):
                self.errors += (f"User keyword '{self.name}' contains no keywords.",)


class If(HeaderAndBody):
    """Represents IF structures in the model.

    Used with IF, Inline IF, ELSE IF and ELSE nodes. The :attr:`type` attribute
    specifies the type.
    """
    _fields = ('header', 'body', 'orelse', 'end')

    def __init__(self, header, body=None, orelse=None, end=None, errors=()):
        super().__init__(header, body, errors)
        self.orelse = orelse
        self.end = end

    @property
    def type(self):
        return self.header.type

    @property
    def condition(self):
        return self.header.condition

    @property
    def assign(self):
        return self.header.assign

    def validate(self, ctx: 'ValidationContext'):
        self._validate_body()
        if self.type == Token.IF:
            self._validate_structure()
            self._validate_end()
        if self.type == Token.INLINE_IF:
            self._validate_structure()
            self._validate_inline_if()

    def _validate_body(self):
        if self._body_is_empty():
            type = self.type if self.type != Token.INLINE_IF else 'IF'
            self.errors += (f'{type} branch cannot be empty.',)

    def _validate_structure(self):
        orelse = self.orelse
        else_seen = False
        while orelse:
            if else_seen:
                if orelse.type == Token.ELSE:
                    error = 'Only one ELSE allowed.'
                else:
                    error = 'ELSE IF not allowed after ELSE.'
                if error not in self.errors:
                    self.errors += (error,)
            else_seen = else_seen or orelse.type == Token.ELSE
            orelse = orelse.orelse

    def _validate_end(self):
        if not self.end:
            self.errors += ('IF must have closing END.',)

    def _validate_inline_if(self):
        branch = self
        assign = branch.assign
        while branch:
            if branch.body:
                item = branch.body[0]
                if assign and item.type != Token.KEYWORD:
                    self.errors += ('Inline IF with assignment can only contain '
                                    'keyword calls.',)
                if getattr(item, 'assign', None):
                    self.errors += ('Inline IF branches cannot contain assignments.',)
                if item.type == Token.INLINE_IF:
                    self.errors += ('Inline IF cannot be nested.',)
            branch = branch.orelse


class For(HeaderAndBody):
    _fields = ('header', 'body', 'end')

    def __init__(self, header, body=None, end=None, errors=()):
        super().__init__(header, body, errors)
        self.end = end

    @property
    def variables(self):
        return self.header.variables

    @property
    def values(self):
        return self.header.values

    @property
    def flavor(self):
        return self.header.flavor

    @property
    def start(self):
        return self.header.start

    @property
    def mode(self):
        return self.header.mode

    @property
    def fill(self):
        return self.header.fill

    def validate(self, ctx: 'ValidationContext'):
        if self._body_is_empty():
            self.errors += ('FOR loop cannot be empty.',)
        if not self.end:
            self.errors += ('FOR loop must have closing END.',)


class Try(HeaderAndBody):
    _fields = ('header', 'body', 'next', 'end')

    def __init__(self, header, body=None, next=None, end=None, errors=()):
        super().__init__(header, body, errors)
        self.next = next
        self.end = end

    @property
    def type(self):
        return self.header.type

    @property
    def patterns(self):
        return getattr(self.header, 'patterns', ())

    @property
    def pattern_type(self):
        return getattr(self.header, 'pattern_type', None)

    @property
    def variable(self):
        return getattr(self.header, 'variable', None)

    def validate(self, ctx: 'ValidationContext'):
        self._validate_body()
        if self.type == Token.TRY:
            self._validate_structure()
            self._validate_end()

    def _validate_body(self):
        if self._body_is_empty():
            self.errors += (f'{self.type} branch cannot be empty.',)

    def _validate_structure(self):
        else_count = 0
        finally_count = 0
        except_count = 0
        empty_except_count = 0
        branch = self.next
        while branch:
            if branch.type == Token.EXCEPT:
                if else_count:
                    self.errors += ('EXCEPT not allowed after ELSE.',)
                if finally_count:
                    self.errors += ('EXCEPT not allowed after FINALLY.',)
                if branch.patterns and empty_except_count:
                    self.errors += ('EXCEPT without patterns must be last.',)
                if not branch.patterns:
                    empty_except_count += 1
                except_count += 1
            if branch.type == Token.ELSE:
                if finally_count:
                    self.errors += ('ELSE not allowed after FINALLY.',)
                else_count += 1
            if branch.type == Token.FINALLY:
                finally_count += 1
            branch = branch.next
        if finally_count > 1:
            self.errors += ('Only one FINALLY allowed.',)
        if else_count > 1:
            self.errors += ('Only one ELSE allowed.',)
        if empty_except_count > 1:
            self.errors += ('Only one EXCEPT without patterns allowed.',)
        if not (except_count or finally_count):
            self.errors += ('TRY structure must have EXCEPT or FINALLY branch.',)

    def _validate_end(self):
        if not self.end:
            self.errors += ('TRY must have closing END.',)


class While(HeaderAndBody):
    _fields = ('header', 'body', 'end')

    def __init__(self, header, body=None, end=None, errors=()):
        super().__init__(header, body, errors)
        self.end = end

    @property
    def condition(self):
        return self.header.condition

    @property
    def limit(self):
        return self.header.limit

    @property
    def on_limit_message(self):
        return self.header.on_limit_message

    def validate(self, ctx: 'ValidationContext'):
        if self._body_is_empty():
            self.errors += ('WHILE loop cannot be empty.',)
        if not self.end:
            self.errors += ('WHILE loop must have closing END.',)


class ModelWriter(ModelVisitor):

    def __init__(self, output):
        if is_string(output) or is_pathlike(output):
            self.writer = file_writer(output)
            self.close_writer = True
        else:
            self.writer = output
            self.close_writer = False

    def write(self, model: Block):
        try:
            self.visit(model)
        finally:
            if self.close_writer:
                self.writer.close()

    def visit_Statement(self, statement: Statement):
        for token in statement.tokens:
            self.writer.write(token.value)


class ModelValidator(ModelVisitor):

    def __init__(self):
        self.ctx = ValidationContext()

    def visit_Block(self, node: Block):
        with self.ctx.block(node):
            node.validate(self.ctx)
            super().generic_visit(node)

    def visit_Statement(self, node: Statement):
        node.validate(self.ctx)


class ValidationContext:

    def __init__(self):
        self.blocks = []

    @contextmanager
    def block(self, node: Block):
        self.blocks.append(node)
        try:
            yield
        finally:
            self.blocks.pop()

    @property
    def parent_block(self):
        return self.blocks[-1] if self.blocks else None

    @property
    def in_keyword(self):
        return any(isinstance(b, Keyword) for b in self.blocks)

    @property
    def in_loop(self):
        return any(isinstance(b, (For, While)) for b in self.blocks)

    @property
    def in_finally(self):
        parent = self.parent_block
        return isinstance(parent, Try) and parent.header.type == Token.FINALLY


class FirstStatementFinder(ModelVisitor):

    def __init__(self):
        self.statement = None

    @classmethod
    def find_from(cls, model):
        finder = cls()
        finder.visit(model)
        return finder.statement

    def visit_Statement(self, statement):
        if self.statement is None:
            self.statement = statement

    def generic_visit(self, node):
        if self.statement is None:
            super().generic_visit(node)


class LastStatementFinder(ModelVisitor):

    def __init__(self):
        self.statement = None

    @classmethod
    def find_from(cls, model):
        finder = cls()
        finder.visit(model)
        return finder.statement

    def visit_Statement(self, statement):
        self.statement = statement
