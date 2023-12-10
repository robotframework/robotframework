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

from pathlib import Path
from typing import Any, Literal, Sequence, TYPE_CHECKING

from robot.model import ModelObject, Tags
from robot.utils import eq, getshortdoc, setter

from .arguments import ArgInfo, ArgumentSpec, EmbeddedArguments
from .model import BodyItemParent, Keyword

if TYPE_CHECKING:
    from .librarykeywordrunner import LibraryKeywordRunner
    from .resourcemodel import ResourceFile
    from .testlibraries import TestLibrary
    from .userkeywordrunner import UserKeywordRunner


class KeywordImplementation(ModelObject):
    """Base class for library and user keyword model objects."""
    USER_KEYWORD = 'USER KEYWORD'
    LIBRARY_KEYWORD = 'LIBRARY KEYWORD'
    INVALID_KEYWORD = 'INVALID KEYWORD'
    repr_args = ('name', 'args')
    __slots__ = ['embedded', '_doc', '_lineno', 'owner', 'parent', 'error']
    type: Literal['USER KEYWORD', 'LIBRARY KEYWORD', 'INVALID KEYWORD']
    source: 'Path|None'
    lineno: 'int|None'    # FIXME: This always be positive int.

    def __init__(self, name: str = '',
                 args: 'ArgumentSpec|None' = None,
                 doc: str = '',
                 tags: 'Tags|Sequence[str]' = (),
                 lineno: 'int|None' = None,
                 owner: 'ResourceFile|TestLibrary|None' = None,
                 parent: 'BodyItemParent|None' = None,
                 error: 'str|None' = None):
        self.embedded: EmbeddedArguments | None = None
        self.name = name
        self.args = args
        self._doc = doc
        self.tags = tags
        self._lineno = lineno
        self.owner = owner
        self.parent = parent
        self.error = error

    @setter
    def name(self, name: str) -> str:
        self.embedded = EmbeddedArguments.from_name(name)
        return name

    @property
    def full_name(self) -> str:
        if self.owner and self.owner.name:
            return f'{self.owner.name}.{self.name}'
        return self.name

    @setter
    def args(self, spec: 'ArgumentSpec|None') -> ArgumentSpec:
        if spec is None:
            spec = ArgumentSpec()
        spec.name = lambda: self.full_name
        return spec

    @property
    def doc(self) -> str:
        return self._doc

    @doc.setter
    def doc(self, doc: str):
        self._doc = doc

    @property
    def short_doc(self) -> str:
        return getshortdoc(self.doc)

    @setter
    def tags(self, tags: 'Tags|Sequence[str]') -> Tags:
        return Tags(tags)

    @property
    def lineno(self) -> int:
        return self._lineno

    @lineno.setter
    def lineno(self, lineno):
        self._lineno = lineno

    @property
    def private(self) -> bool:
        return bool(self.tags and self.tags.robot('private'))

    @property
    def source(self) -> 'Path|None':
        return self.owner.source if self.owner is not None else None

    def matches(self, name: str) -> bool:
        if self.embedded:
            return self.embedded.match(name)
        return eq(self.name, name, ignore='_')

    def create_runner(self, name, languages=None) \
            -> 'LibraryKeywordRunner|UserKeywordRunner':
        raise NotImplementedError

    def bind(self, data: Keyword) -> 'KeywordImplementation':
        raise NotImplementedError

    def _include_in_repr(self, name: str, value: Any) -> bool:
        return name == 'name' or value

    def _repr_format(self, name: str, value: Any) -> str:
        if name == 'args':
            value = [self._decorate_arg(a) for a in self.args]
        return super()._repr_format(name, value)

    def _decorate_arg(self, arg: ArgInfo) -> str:
        return str(arg)
