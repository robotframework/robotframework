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

import warnings
from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from typing import cast, Iterator, Sequence, TextIO, Union

from robot.utils import file_writer, test_or_task

from .statements import (Break, Continue, ElseHeader, ElseIfHeader, End, ExceptHeader,
                         Error, FinallyHeader, ForHeader, IfHeader, KeywordCall,
                         KeywordName, Node, ReturnSetting, ReturnStatement,
                         SectionHeader, Statement, TemplateArguments, TestCaseName,
                         TryHeader, Var, WhileHeader)
from .visitor import ModelVisitor
from ..lexer import Token


Body = Sequence[Union[Statement, 'Block']]
Errors = Sequence[str]


class Container(Node, ABC):

    @property
    def lineno(self) -> int:
        statement = FirstStatementFinder.find_from(self)
        return statement.lineno if statement else -1

    @property
    def col_offset(self) -> int:
        statement = FirstStatementFinder.find_from(self)
        return statement.col_offset if statement else -1

    @property
    def end_lineno(self) -> int:
        statement = LastStatementFinder.find_from(self)
        return statement.end_lineno if statement else -1

    @property
    def end_col_offset(self) -> int:
        statement = LastStatementFinder.find_from(self)
        return statement.end_col_offset if statement else -1

    def validate_model(self):
        ModelValidator().visit(self)

    def validate(self, ctx: 'ValidationContext'):
        pass


class File(Container):
    _fields = ('sections',)
    _attributes = ('source', 'languages') + Container._attributes

    def __init__(self, sections: 'Sequence[Section]' = (), source: 'Path|None' = None,
                 languages: Sequence[str] = ()):
        super().__init__()
        self.sections = list(sections)
        self.source = source
        self.languages = list(languages)

    def save(self, output: 'Path|str|TextIO|None' = None):
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


class Block(Container, ABC):
    _fields = ('header', 'body')

    def __init__(self, header: 'Statement|None', body: Body = (), errors: Errors = ()):
        self.header = header
        self.body = list(body)
        self.errors = tuple(errors)

    def _body_is_empty(self):
        # This works with tests, keywords, and blocks inside them, not with sections.
        valid = (KeywordCall, TemplateArguments, Var, Continue, Break, ReturnSetting,
                 ReturnStatement, NestedBlock, Error)
        return not any(isinstance(node, valid) for node in self.body)


class Section(Block):
    header: 'SectionHeader|None'


class SettingSection(Section):
    header: SectionHeader


class VariableSection(Section):
    header: SectionHeader


# TODO: should there be a separate TaskSection?
class TestCaseSection(Section):
    header: SectionHeader

    @property
    def tasks(self) -> bool:
        return self.header.type == Token.TASK_HEADER


class KeywordSection(Section):
    header: SectionHeader


class CommentSection(Section):
    header: 'SectionHeader|None'


class ImplicitCommentSection(CommentSection):
    header: None

    def __init__(self, header: 'Statement|None' = None, body: Body = (),
                 errors: Errors = ()):
        body = ([header] if header is not None else []) + list(body)
        super().__init__(None, body, errors)


class InvalidSection(Section):
    pass


class TestCase(Block):
    header: TestCaseName

    @property
    def name(self) -> str:
        return self.header.name

    def validate(self, ctx: 'ValidationContext'):
        if self._body_is_empty():
            self.errors += (test_or_task('{Test} cannot be empty.', ctx.tasks),)


class Keyword(Block):
    header: KeywordName

    @property
    def name(self) -> str:
        return self.header.name

    def validate(self, ctx: 'ValidationContext'):
        if self._body_is_empty():
            self.errors += ("User keyword cannot be empty.",)


class NestedBlock(Block):
    _fields = ('header', 'body', 'end')

    def __init__(self, header: Statement, body: Body = (), end: 'End|None' = None,
                 errors: Errors = ()):
        super().__init__(header, body, errors)
        self.end = end


class If(NestedBlock):
    """Represents IF structures in the model.

    Used with IF, Inline IF, ELSE IF and ELSE nodes. The :attr:`type` attribute
    specifies the type.
    """
    _fields = ('header', 'body', 'orelse', 'end')
    header: 'IfHeader|ElseIfHeader|ElseHeader'

    def __init__(self, header: Statement, body: Body = (), orelse: 'If|None' = None,
                 end: 'End|None' = None, errors: Errors = ()):
        super().__init__(header, body, end, errors)
        self.orelse = orelse

    @property
    def type(self) -> str:
        return self.header.type

    @property
    def condition(self) -> 'str|None':
        return self.header.condition

    @property
    def assign(self) -> 'tuple[str, ...]':
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
                item = cast(Statement, branch.body[0])
                if assign and item.type != Token.KEYWORD:
                    self.errors += ('Inline IF with assignment can only contain '
                                    'keyword calls.',)
                if getattr(item, 'assign', None):
                    self.errors += ('Inline IF branches cannot contain assignments.',)
                if item.type == Token.INLINE_IF:
                    self.errors += ('Inline IF cannot be nested.',)
            branch = branch.orelse


class For(NestedBlock):
    header: ForHeader

    @property
    def assign(self) -> 'tuple[str, ...]':
        return self.header.assign

    @property
    def variables(self) -> 'tuple[str, ...]':    # TODO: Remove in RF 8.0.
        warnings.warn("'For.variables' is deprecated and will be removed in "
                      "Robot Framework 8.0. Use 'For.assign' instead.")
        return self.assign

    @property
    def values(self) -> 'tuple[str, ...]':
        return self.header.values

    @property
    def flavor(self) -> 'str|None':
        return self.header.flavor

    @property
    def start(self) -> 'str|None':
        return self.header.start

    @property
    def mode(self) -> 'str|None':
        return self.header.mode

    @property
    def fill(self) -> 'str|None':
        return self.header.fill

    def validate(self, ctx: 'ValidationContext'):
        if self._body_is_empty():
            self.errors += ('FOR loop cannot be empty.',)
        if not self.end:
            self.errors += ('FOR loop must have closing END.',)


class Try(NestedBlock):
    _fields = ('header', 'body', 'next', 'end')
    header: 'TryHeader|ExceptHeader|ElseHeader|FinallyHeader'

    def __init__(self, header: Statement, body: Body = (), next: 'Try|None' = None,
                 end: 'End|None' = None, errors: Errors = ()):
        super().__init__(header, body, end, errors)
        self.next = next

    @property
    def type(self) -> str:
        return self.header.type

    @property
    def patterns(self) -> 'tuple[str, ...]':
        return getattr(self.header, 'patterns', ())

    @property
    def pattern_type(self) -> 'str|None':
        return getattr(self.header, 'pattern_type', None)

    @property
    def assign(self) -> 'str|None':
        return getattr(self.header, 'assign', None)

    @property
    def variable(self) -> 'str|None':    # TODO: Remove in RF 8.0.
        warnings.warn("'Try.variable' is deprecated and will be removed in "
                      "Robot Framework 8.0. Use 'Try.assign' instead.")
        return self.assign

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


class While(NestedBlock):
    header: WhileHeader

    @property
    def condition(self) -> str:
        return self.header.condition

    @property
    def limit(self) -> 'str|None':
        return self.header.limit

    @property
    def on_limit(self) -> 'str|None':
        return self.header.on_limit

    @property
    def on_limit_message(self) -> 'str|None':
        return self.header.on_limit_message

    def validate(self, ctx: 'ValidationContext'):
        if self._body_is_empty():
            self.errors += ('WHILE loop cannot be empty.',)
        if not self.end:
            self.errors += ('WHILE loop must have closing END.',)


class ModelWriter(ModelVisitor):

    def __init__(self, output: 'Path|str|TextIO'):
        if isinstance(output, (Path, str)):
            self.writer = file_writer(output)
            self.close_writer = True
        else:
            self.writer = output
            self.close_writer = False

    def write(self, model: Node):
        try:
            self.visit(model)
        finally:
            if self.close_writer:
                self.writer.close()

    def visit_Statement(self, statement: Statement):
        for token in statement:
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
    def block(self, node: Block) -> Iterator[None]:
        self.blocks.append(node)
        try:
            yield
        finally:
            self.blocks.pop()

    @property
    def parent_block(self) -> 'Block|None':
        return self.blocks[-1] if self.blocks else None

    @property
    def tasks(self) -> bool:
        for parent in self.blocks:
            if isinstance(parent, TestCaseSection):
                return parent.tasks
        return False

    @property
    def in_keyword(self) -> bool:
        return any(isinstance(b, Keyword) for b in self.blocks)

    @property
    def in_loop(self) -> bool:
        return any(isinstance(b, (For, While)) for b in self.blocks)

    @property
    def in_finally(self) -> bool:
        parent = self.parent_block
        return isinstance(parent, Try) and parent.header.type == Token.FINALLY


class FirstStatementFinder(ModelVisitor):

    def __init__(self):
        self.statement: 'Statement|None' = None

    @classmethod
    def find_from(cls, model: Node) -> 'Statement|None':
        finder = cls()
        finder.visit(model)
        return finder.statement

    def visit_Statement(self, statement: Statement):
        if self.statement is None:
            self.statement = statement

    def generic_visit(self, node: Node):
        if self.statement is None:
            super().generic_visit(node)


class LastStatementFinder(ModelVisitor):

    def __init__(self):
        self.statement: 'Statement|None' = None

    @classmethod
    def find_from(cls, model: Node) -> 'Statement|None':
        finder = cls()
        finder.visit(model)
        return finder.statement

    def visit_Statement(self, statement: Statement):
        self.statement = statement
