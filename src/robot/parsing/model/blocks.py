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
from .statements import Else, ElseIfStatement, KeywordCall

from .visitor import ModelVisitor


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


class IfBlock(Block):
    _fields = ('header', 'body', 'end')
    _attributes = Block._attributes + ('error',)

    def __init__(self, header, body=None, end=None, error=None):
        self.header = header
        self.body = body or []
        self.end = end
        self.error = error

    @property
    def variables(self):
        return self.header.variables

    @property
    def value(self):
        return self.header.value

    @property
    def _header(self):
        return self.header._header

    @property
    def _end(self):
        return self.end.value if self.end else None

    def validate(self):
        errors = self._validate()
        if not errors:
            self.error = None
        elif len(errors) == 1:
            self.error = 'IF has ' + errors[0][0].lower() + errors[0][1:]
        else:
            self.error = 'IF has multiple errors:\n- ' + '\n- '.join(errors)

    def _validate(self):
        errors = []
        if not self.end:
            errors.append("No closing 'END'.")
        else_seen = False
        last_is_normal_step = False
        for step in self.body:
            if isinstance(step, Else):
                if else_seen:
                    errors.append("Multiple 'ELSE' branches.")
                if not last_is_normal_step:
                    errors.append("Empty branch.")
                else_seen = True
                last_is_normal_step = False
            elif isinstance(step, ElseIfStatement):
                if else_seen:
                    errors.append("'ELSE IF' after 'ELSE'.")
                if not last_is_normal_step:
                    errors.append("Empty branch.")
                last_is_normal_step = False
            else:
                last_is_normal_step = True
        if not last_is_normal_step:
            errors.append("Empty branch.")
        return errors


class ForLoop(Block):
    _fields = ('header', 'body', 'end')
    _attributes = Block._attributes + ('error',)

    def __init__(self, header, body=None, end=None, error=None):
        self.header = header
        self.body = body or []
        self.end = end
        self.error = error

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
        errors = self._validate()
        if not errors:
            self.error = None
        elif len(errors) == 1:
            self.error = 'FOR loop has ' + errors[0][0].lower() + errors[0][1:]
        else:
            self.error = 'FOR loop has multiple errors:\n- ' + '\n- '.join(errors)

    def _validate(self):
        errors = []
        if not self.variables:
            errors.append('No loop variables.')
        if not self.flavor:
            errors.append("No 'IN' or other valid separator.")
        else:
            for var in self.variables:
                if not is_scalar_assign(var):
                    errors.append("Invalid loop variable '%s'." % var)
            if not self.values:
                errors.append('No loop values.')
        if not self.body:
            errors.append('Empty body.')
        if not self.end:
            errors.append("No closing 'END'.")
        return errors


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

    def visit_IfBlock(self, node):
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
