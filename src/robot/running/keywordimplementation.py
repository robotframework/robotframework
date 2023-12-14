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
    """Base class for different keyword implementations."""
    USER_KEYWORD = 'USER KEYWORD'
    LIBRARY_KEYWORD = 'LIBRARY KEYWORD'
    INVALID_KEYWORD = 'INVALID KEYWORD'
    repr_args = ('name', 'args')
    __slots__ = ['embedded', '_name', '_doc', '_lineno', 'owner', 'parent', 'error']
    type: Literal['USER KEYWORD', 'LIBRARY KEYWORD', 'INVALID KEYWORD']

    def __init__(self, name: str = '',
                 args: 'ArgumentSpec|None' = None,
                 doc: str = '',
                 tags: 'Tags|Sequence[str]' = (),
                 lineno: 'int|None' = None,
                 owner: 'ResourceFile|TestLibrary|None' = None,
                 parent: 'BodyItemParent|None' = None,
                 error: 'str|None' = None):
        self._name = name
        self.embedded = self._get_embedded(name)
        self.args = args
        self._doc = doc
        self.tags = tags
        self._lineno = lineno
        self.owner = owner
        self.parent = parent
        self.error = error

    def _get_embedded(self, name) -> 'EmbeddedArguments|None':
        return EmbeddedArguments.from_name(name)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self.embedded = self._get_embedded(name)
        if self.owner and self._name:
            self.owner.keyword_finder.invalidate_cache()
        self._name = name

    @property
    def full_name(self) -> str:
        if self.owner and self.owner.name:
            return f'{self.owner.name}.{self.name}'
        return self.name

    @setter
    def args(self, spec: 'ArgumentSpec|None') -> ArgumentSpec:
        """Information about accepted arguments.

        It would be more correct to use term *parameter* instead of
        *argument* in this context, and this attribute may be renamed
        accordingly in the future. A forward compatible :attr:`params`
        attribute exists already now.
        """
        if spec is None:
            spec = ArgumentSpec()
        spec.name = lambda: self.full_name
        return spec

    @property
    def params(self) -> ArgumentSpec:
        """Keyword parameter information.

        This is a forward compatible alias for :attr:`args`.
        """
        return self.args

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
    def lineno(self) -> 'int|None':
        return self._lineno

    @lineno.setter
    def lineno(self, lineno: 'int|None'):
        self._lineno = lineno

    @property
    def private(self) -> bool:
        return bool(self.tags and self.tags.robot('private'))

    @property
    def source(self) -> 'Path|None':
        return self.owner.source if self.owner is not None else None

    def matches(self, name: str) -> bool:
        """Returns true if ``name`` matches the keyword name.

        With normal keywords matching is a case, space and underscore insensitive
        string comparison. With keywords accepting embedded arguments, matching
        is done against the name.
        """
        if self.embedded:
            return self.embedded.match(name) is not None
        return eq(self.name, name, ignore='_')

    def resolve_arguments(self, args: Sequence[str], variables=None,
                          languages=None) -> 'tuple[list, list]':
        return self.args.resolve(args, variables, languages=languages)

    def create_runner(self, name: 'str|None', languages=None) \
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
