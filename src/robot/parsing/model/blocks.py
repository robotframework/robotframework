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

from robot.utils import file_writer, is_pathlike, is_string, normalize_whitespace

from .visitor import ModelVisitor


class ModelWriter(ModelVisitor):

    def __init__(self, output):
        self.output = output

    def visit_Statement(self, statement):
        for line in statement.lines:
            for token in line:
                self.output.write(token.value)


class Block(ast.AST):
    _fields = ()


class File(Block):
    _fields = ('sections',)

    def __init__(self, sections=None, source=None):
        self.sections = sections or []
        self.source = source

    @property
    def has_tests(self):
        return any(isinstance(s, TestCaseSection) for s in self.sections)

    def save(self, output=None):
        output = output or self.source
        if output is None:
            raise TypeError('Saving model requires explicit output '
                            'when original source is not path.')
        if is_string(output) or is_pathlike(output):
            output = file_writer(output)
            close = True
        else:
            close = False
        try:
            ModelWriter(output).visit(self)
        finally:
            if close:
                output.close()


class Section(Block):
    _fields = ('header', 'body')

    def __init__(self, header=None, body=None):
        self.header = header
        self.body = Body(body)


class SettingSection(Section):
    pass


class VariableSection(Section):
    pass


class TestCaseSection(Section):

    @property
    def tasks(self):
        header = normalize_whitespace(self.header.data_tokens[0].value)
        return header.strip('* ').upper() in ('TASKS', 'TASK')


class KeywordSection(Section):
    pass


class CommentSection(Section):
    pass


class Body(Block):
    _fields = ('items',)

    def __init__(self, items=None):
        self.items = items or []

    def add(self, item):
        self.items.append(item)


class TestCase(Block):
    _fields = ('header', 'body')

    def __init__(self, header, body=None):
        self.header = header
        self.body = Body(body)

    @property
    def name(self):
        return self.header.name


class Keyword(Block):
    _fields = ('header', 'body')

    def __init__(self, header, body=None):
        self.header = header
        self.body = Body(body)

    @property
    def name(self):
        return self.header.name


class ForLoop(Block):
    _fields = ('header', 'body', 'end')

    def __init__(self, header):
        self.header = header
        self.body = Body()
        self.end = None

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
    def _header(self):
        return self.header._header

    @property
    def _end(self):
        return self.end.value if self.end else None
