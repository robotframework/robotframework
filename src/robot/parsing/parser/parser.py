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

from typing import Callable, Iterator

from robot.conf import LanguagesLike
from robot.utils import Source

from ..lexer import get_init_tokens, get_resource_tokens, get_tokens, Token
from ..model import Config, File, ModelVisitor, Statement
from .blockparsers import Parser
from .fileparser import FileParser


def get_model(
    source: Source,
    data_only: bool = False,
    curdir: "str|None" = None,
    lang: LanguagesLike = None,
) -> File:
    """Parses the given source into a model represented as an AST.

    How to use the model is explained more thoroughly in the general
    documentation of the :mod:`robot.parsing` module.

    :param source: The source where to read the data. Can be a path to
        a source file as a string or as ``pathlib.Path`` object, an already
        opened file object, or Unicode text containing the date directly.
        Source files must be UTF-8 encoded.
    :param data_only: When ``False`` (default), returns all tokens. When set
        to ``True``, omits separators, comments, continuation markers, and
        other non-data tokens. Model like this cannot be saved back to
        file system.
    :param curdir: Directory where the source file exists. This path is used
        to set the value of the built-in ``${CURDIR}`` variable during parsing.
        When not given, the variable is left as-is. Should only be given
        only if the model will be executed afterward. If the model is saved
        back to disk, resolving ``${CURDIR}`` is typically not a good idea.
    :param lang: Additional languages to be supported during parsing.
        Can be a string matching any of the supported language codes or names,
        an initialized :class:`~robot.conf.languages.Language` subclass,
        a list containing such strings or instances, or a
        :class:`~robot.conf.languages.Languages` instance.

    Use :func:`get_resource_model` or :func:`get_init_model` when parsing
    resource or suite initialization files, respectively.
    """
    return _get_model(get_tokens, source, data_only, curdir, lang)


def get_resource_model(
    source: Source,
    data_only: bool = False,
    curdir: "str|None" = None,
    lang: LanguagesLike = None,
) -> File:
    """Parses the given source into a resource file model.

    Same as :func:`get_model` otherwise, but the source is considered to be
    a resource file. This affects, for example, what settings are valid.
    """
    return _get_model(get_resource_tokens, source, data_only, curdir, lang)


def get_init_model(
    source: Source,
    data_only: bool = False,
    curdir: "str|None" = None,
    lang: LanguagesLike = None,
) -> File:
    """Parses the given source into an init file model.

    Same as :func:`get_model` otherwise, but the source is considered to be
    a suite initialization file. This affects, for example, what settings are
    valid.
    """
    return _get_model(get_init_tokens, source, data_only, curdir, lang)


def _get_model(
    token_getter: Callable[..., Iterator[Token]],
    source: Source,
    data_only: bool,
    curdir: "str|None",
    lang: LanguagesLike,
):
    tokens = token_getter(source, data_only, lang=lang)
    statements = _tokens_to_statements(tokens, curdir)
    model = _statements_to_model(statements, source)
    ConfigParser.parse(model)
    model.validate_model()
    return model


def _tokens_to_statements(
    tokens: Iterator[Token],
    curdir: "str|None",
) -> Iterator[Statement]:
    statement = []
    EOS = Token.EOS
    for t in tokens:
        if curdir and "${CURDIR}" in t.value:
            t.value = t.value.replace("${CURDIR}", curdir)
        if t.type != EOS:
            statement.append(t)
        else:
            yield Statement.from_tokens(statement)
            statement = []


def _statements_to_model(statements: Iterator[Statement], source: Source) -> File:
    root = FileParser(source=source)
    stack: "list[Parser]" = [root]
    for statement in statements:
        while not stack[-1].handles(statement):
            stack.pop()
        parser = stack[-1].parse(statement)
        if parser:
            stack.append(parser)
    return root.model


class ConfigParser(ModelVisitor):

    def __init__(self, model: File):
        self.model = model

    @classmethod
    def parse(cls, model: File):
        # Only implicit comment sections can contain configs. They have no header.
        if model.sections and model.sections[0].header is None:
            cls(model).visit(model.sections[0])

    def visit_Config(self, node: Config):
        language = node.language
        if language:
            self.model.languages.append(language.code)
