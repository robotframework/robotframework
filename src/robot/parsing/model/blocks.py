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

from .statements import Comment, EmptyLine
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

    def validate(self, context):
        pass

    def _body_is_empty(self):
        for node in self.body:
            if not isinstance(node, (EmptyLine, Comment)):
                return False
        return True


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

    def validate(self, context):
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

    def validate(self, context):
        if self._body_is_empty():
            self.errors += ('FOR loop cannot be empty.',)
        if not self.end:
            self.errors += ('FOR loop must have closing END.',)


class Try(Block):
    _fields = ('header', 'body', 'next', 'end')

    def __init__(self, header, body=None, next=None, end=None, errors=()):
        self.header = header
        self.body = body or []
        self.next = next
        self.end = end
        self.errors = errors

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

    def validate(self, context):
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


class While(Block):
    _fields = ('header', 'body', 'end')

    def __init__(self, header, body=None, end=None, errors=()):
        self.header = header
        self.body = body or []
        self.end = end
        self.errors = errors

    @property
    def condition(self):
        return self.header.condition

    @property
    def limit(self):
        return self.header.limit

    def validate(self, context):
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

    def __init__(self):
        self._context = ValidationContext()

    def visit_Block(self, node):
        self._context.start_block(node)
        node.validate(self._context)
        ModelVisitor.generic_visit(self, node)
        self._context.end_block()

    def visit_Try(self, node):
        if node.header.type == Token.FINALLY:
            self._context.in_finally = True
        self.visit_Block(node)
        self._context.in_finally = False

    def visit_Statement(self, node):
        node.validate(self._context)
        ModelVisitor.generic_visit(self, node)


class ValidationContext:

    def __init__(self):
        self.roots = []
        self.in_finally = False

    def start_block(self, node):
        self.roots.append(node)

    def end_block(self):
        self.roots.pop()

    @property
    def in_keyword(self):
        return Keyword in [type(r) for r in self.roots]

    @property
    def in_for(self):
        return For in [type(r) for r in self.roots]

    @property
    def in_while(self):
        return While in [type(r) for r in self.roots]


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
