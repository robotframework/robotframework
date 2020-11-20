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
from robot.variables import is_scalar_assign

from .visitor import ModelVisitor
from ..lexer import Token


class Block(ast.AST):
    _fields = ()
    _attributes = ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')

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


class File(Block):
    _fields = ('sections',)
    _attributes = ('source',) + Block._attributes

    def __init__(self, sections=None, source=None):
        self.sections = sections or []
        self.source = source

    def validate(self):
        ModelValidator().visit(self)

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
    _fields = ('header', 'body', 'orelse', 'end')
    _attributes = Block._attributes + ('errors',)

    def __init__(self, header, body=None, orelse=None, end=None, errors=None):
        self.header = header
        self.body = body or []
        self.orelse = orelse
        self.end = end
        self.errors = errors or []

    @property
    def type(self):
        return self.header.type

    @property
    def condition(self):
        condition = self.header.condition
        return condition[0] if condition else None

    def validate(self):
        self._validate_header()
        self._validate_body()
        if self.type == Token.IF:
            self._validate_structure()
            self._validate_end()

    def _validate_header(self):
        length = len(self.header.condition)
        error = None
        if self.type in (Token.IF, Token.ELSE_IF):
            if length == 0:
                error = '%s has no condition.' % self.type
            elif length > 1:
                error = '%s has more than one condition.' % self.type
        else:
            if length > 0:
                error = 'ELSE has condition.'
        if error:
            self.errors.append(error)

    def _validate_body(self):
        if not self.body:
            self.errors.append('%s has empty body.' % self.type)

    def _validate_structure(self):
        orelse = self.orelse
        else_seen = False
        while orelse:
            if else_seen:
                if orelse.type == Token.ELSE:
                    self.errors.append('Multiple ELSE branches.')
                else:
                    self.errors.append('ELSE IF after ELSE.')
            else_seen = else_seen or orelse.type == Token.ELSE
            orelse = orelse.orelse

    def _validate_end(self):
        if not self.end:
            self.errors.append('IF has no closing END.')


class ForLoop(Block):
    _fields = ('header', 'body', 'end')
    _attributes = Block._attributes + ('errors',)

    def __init__(self, header, body=None, end=None, errors=None):
        self.header = header
        self.body = body or []
        self.end = end
        self.errors = errors or []

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
        if not self.variables:
            self._add_error('no loop variables')
        if not self.flavor:
            self._add_error("no 'IN' or other valid separator")
        else:
            for var in self.variables:
                if not is_scalar_assign(var):
                    self._add_error("invalid loop variable '%s'" % var)
            if not self.values:
                self._add_error('no loop values')
        if not self.body:
            self._add_error('empty body')
        if not self.end:
            self._add_error("no closing END")

    def _add_error(self, error):
        self.errors.append('FOR loop has %s.' % error)


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

    def visit_ForLoop(self, node):
        node.validate()
        ModelVisitor.generic_visit(self, node)

    def visit_If(self, node):
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
