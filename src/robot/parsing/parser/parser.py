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

from ..lexer import Token, get_tokens, get_resource_tokens, get_init_tokens
from ..model import Statement

from .fileparser import FileParser


def get_model(source, data_only=False, curdir=None):
    """FIXME: Documentation missing.

    Mention TestSuite.from_model when docs are written.
    """
    tokens = get_tokens(source, data_only)
    statements = _tokens_to_statements(tokens, curdir)
    return _statements_to_model(statements, source)


def get_resource_model(source, data_only=False, curdir=None):
    """Parses the given source to a resource file model.

    Otherwise same as :func:`get_model` but the source is considered to be
    a resource file. This affects, for example, what settings are valid.
    """
    tokens = get_resource_tokens(source, data_only)
    statements = _tokens_to_statements(tokens, curdir)
    return _statements_to_model(statements, source)


def get_init_model(source, data_only=False, curdir=None):
    """Parses the given source to a init file model.

    Otherwise same as :func:`get_model` but the source is considered to be
    a suite initialization file. This affects, for example, what settings are
    valid.
    """
    tokens = get_init_tokens(source, data_only)
    statements = _tokens_to_statements(tokens, curdir)
    return _statements_to_model(statements, source)


def _tokens_to_statements(tokens, curdir=None):
    statement = []
    EOS = Token.EOS
    for t in tokens:
        if curdir and '${CURDIR}' in t.value:
            t.value = t.value.replace('${CURDIR}', curdir)
        if t.type != EOS:
            statement.append(t)
        else:
            yield Statement.from_tokens(statement)
            statement = []


def _statements_to_model(statements, source=None):
    parser = FileParser(source=source)
    stack = [parser]
    for statement in statements:
        while not stack[-1].handles(statement):
            stack.pop()
        parser = stack[-1].parse(statement)
        if parser:
            stack.append(parser)
    return stack[0].model
