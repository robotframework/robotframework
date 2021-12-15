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

from robot.utils import file_writer, is_pathlike, is_string

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

    def validate(self):
        pass


class HeaderAndBody(Block):
    _fields = ('header', 'body')

    def __init__(self, header, body=None, errors=()):
        self.header = header
        self.body = body or []
        self.errors = errors


class File(Block):
    _fields = ('sections',)
    _attributes = ('source',) + Block._attributes

    def __init__(self, sections=None, source=None):
        self.sections = sections or []
        self.source = source

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


class Section(Block):
    _fields = ('header', 'body')

    def __init__(self, header=None, body=None):
        self.header = header
        self.body = body or []


class SettingSection(Section):
    pass


class VariableSection(Section):
    pass


class TestCaseSection(Section):

    @property
    def tasks(self):
        return self.header.name.upper() in ('TASKS', 'TASK')


class KeywordSection(Section):
    pass


class CommentSection(Section):
    pass


class TestCase(Block):
    _fields = ('header', 'body')

    def __init__(self, header, body=None):
        self.header = header
        self.body = body or []

    @property
    def name(self):
        return self.header.name


class Keyword(Block):
    _fields = ('header', 'body')

    def __init__(self, header, body=None):
        self.header = header
        self.body = body or []

    @property
    def name(self):
        return self.header.name


class If(Block):
    """Represents IF structures in the model.

    Used with IF, Inline IF, ELSE IF and ELSE nodes. The :attr:`type` attribute
    specifies the type.
    """
    _fields = ('header', 'body', 'orelse', 'end')

    def __init__(self, header, body=None, orelse=None, end=None, errors=()):
        self.header = header
        self.body = body or []
        self.orelse = orelse
        self.end = end
        self.errors = errors

    @property
    def type(self):
        return self.header.type

    @property
    def condition(self):
        return self.header.condition

    @property
    def assign(self):
        return self.header.assign

    def validate(self):
        self._validate_body()
        if self.type == Token.IF:
            self._validate_structure()
            self._validate_end()
        if self.type == Token.INLINE_IF:
            self._validate_structure()
            self._validate_inline_if()

    def _validate_body(self):
        if not self.body:
            type = self.type if self.type != Token.INLINE_IF else 'IF'
            self.errors += (f'{type} branch cannot be empty.',)

    def _validate_structure(self):
        orelse = self.orelse
        else_seen = False
        while orelse:
            if else_seen:
                if orelse.type == Token.ELSE:
                    error = 'Multiple ELSE branches.'
                else:
                    error = 'ELSE IF after ELSE.'
                if error not in self.errors:
                    self.errors += (error,)
            else_seen = else_seen or orelse.type == Token.ELSE
            orelse = orelse.orelse

    def _validate_end(self):
        if not self.end:
            self.errors += ('IF has no closing END.',)

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


class For(Block):
    _fields = ('header', 'body', 'end')

    def __init__(self, header, body=None, end=None, errors=()):
        self.header = header
        self.body = body or []
        self.end = end
        self.errors = errors

    @property
    def variables(self):
        return self.header.variables

    @property
    def values(self):
        return self.header.values

    @property
    def flavor(self):
        return self.header.flavor

    def validate(self):
        if not self.body:
            self.errors += ('FOR loop has empty body.',)
        if not self.end:
            self.errors += ('FOR loop has no closing END.',)


class Try(Block):
    _fields = ('header', 'body', 'blocks', 'end')

    def __init__(self, header, body=None, blocks=None, end=None, errors=()):
        self.header = header
        self.body = body or []
        self.blocks = blocks or []
        self.end = end
        self.errors = errors

    @property
    def except_blocks(self):
        return [b for b in self.blocks if b.type == Token.EXCEPT]

    @property
    def else_block(self):
        else_blocks = [b for b in self.blocks if b.type == Token.ELSE]
        return else_blocks[0] if else_blocks else None

    @property
    def finally_block(self):
        finally_blocks = [b for b in self.blocks if b.type == Token.FINALLY]
        return finally_blocks[0] if finally_blocks else None

    def validate(self):
        if not self.end:
            self.errors += ('TRY has no closing END.',)
        if not self.body:
            self.errors += ('TRY block cannot be empty.',)
        if not (self.except_blocks or self.finally_block):
            self.errors += ('TRY block must be followed by EXCEPT or FINALLY block"',)
        self._validate_structure()

    def _validate_structure(self):
        else_count = 0
        finally_count = 0
        default_block_seen = False
        for block in self.blocks:
            if block.type == Token.EXCEPT:
                if else_count > 0:
                    self.errors += ('ELSE block before EXCEPT block.',)
                if finally_count > 0:
                    self.errors += ('FINALLY block before EXCEPT block.',)
                if not block.patterns:
                    if default_block_seen:
                        self.errors += ('Multiple default (empty) EXCEPT blocks',)
                    default_block_seen = True
                if block.patterns and default_block_seen:
                    self.errors += ('Default (empty) EXCEPT must be last.',)
            if block.type == Token.ELSE:
                else_count += 1
                if finally_count > 0:
                    self.errors += ('FINALLY block before ELSE block.',)
            if block.type == Token.FINALLY:
                finally_count += 1
        if finally_count > 1:
            self.errors += ('Multiple FINALLY blocks.',)
        if else_count > 1:
            self.errors += ('Multiple ELSE blocks.',)


class TryHandler(HeaderAndBody):

    @property
    def type(self):
        return self.header.type

    @property
    def patterns(self):
        return getattr(self.header, 'patterns', [])

    @property
    def variable(self):
        return getattr(self.header, 'variable', None)

    def validate(self):
        if not self.body:
            self.errors += (f'{self.type} block cannot be empty.',)


class ModelWriter(ModelVisitor):

    def __init__(self, output):
        if is_string(output) or is_pathlike(output):
            self.writer = file_writer(output)
            self.close_writer = True
        else:
            self.writer = output
            self.close_writer = False

    def write(self, model):
        try:
            self.visit(model)
        finally:
            if self.close_writer:
                self.writer.close()

    def visit_Statement(self, statement):
        for token in statement.tokens:
            self.writer.write(token.value)


class ModelValidator(ModelVisitor):

    def visit_Block(self, node):
        node.validate()
        ModelVisitor.generic_visit(self, node)

    def visit_Statement(self, node):
        node.validate()
        ModelVisitor.generic_visit(self, node)


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
            ModelVisitor.generic_visit(self, node)


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
