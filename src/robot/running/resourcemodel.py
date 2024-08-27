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
from typing import Any, Iterable, Literal, overload, Sequence, TYPE_CHECKING

from robot import model
from robot.model import BodyItem, create_fixture, DataDict, ModelObject, Tags
from robot.output import LOGGER
from robot.utils import NOT_SET, setter

from .arguments import ArgInfo, ArgumentSpec, UserKeywordArgumentParser
from .keywordimplementation import KeywordImplementation
from .keywordfinder import KeywordFinder
from .model import Body, BodyItemParent, Keyword, TestSuite
from .userkeywordrunner import UserKeywordRunner, EmbeddedArgumentsRunner

if TYPE_CHECKING:
    from robot.conf import LanguagesLike
    from robot.parsing import File


class ResourceFile(ModelObject):
    """Represents a resource file."""

    repr_args = ('source',)
    __slots__ = ('_source', 'owner', 'doc', 'keyword_finder')

    def __init__(self, source: 'Path|str|None' = None,
                 owner: 'TestSuite|None' = None,
                 doc: str = ''):
        self.source = source
        self.owner = owner
        self.doc = doc
        self.keyword_finder = KeywordFinder['UserKeyword'](self)
        self.imports = []
        self.variables = []
        self.keywords = []

    @property
    def source(self) -> 'Path|None':
        if self._source:
            return self._source
        if self.owner:
            return self.owner.source
        return None

    @source.setter
    def source(self, source: 'Path|str|None'):
        if isinstance(source, str):
            source = Path(source)
        self._source = source

    @property
    def name(self) -> 'str|None':
        """Resource file name.

        ``None`` if resource file is part of a suite or if it does not have
        :attr:`source`, name of the source file without the extension otherwise.
        """
        if self.owner or not self.source:
            return None
        return self.source.stem

    @setter
    def imports(self, imports: Sequence['Import']) -> 'Imports':
        return Imports(self, imports)

    @setter
    def variables(self, variables: Sequence['Variable']) -> 'Variables':
        return Variables(self, variables)

    @setter
    def keywords(self, keywords: Sequence['UserKeyword']) -> 'UserKeywords':
        return UserKeywords(self, keywords)

    @classmethod
    def from_file_system(cls, path: 'Path|str', **config) -> 'ResourceFile':
        """Create a :class:`ResourceFile` object based on the give ``path``.

        :param path: File path where to read the data from.
        :param config: Configuration parameters for :class:`~.builders.ResourceFileBuilder`
            class that is used internally for building the suite.

        New in Robot Framework 6.1. See also :meth:`from_string` and :meth:`from_model`.
        """
        from .builder import ResourceFileBuilder
        return ResourceFileBuilder(**config).build(path)

    @classmethod
    def from_string(cls, string: str, **config) -> 'ResourceFile':
        """Create a :class:`ResourceFile` object based on the given ``string``.

        :param string: String to create the resource file from.
        :param config: Configuration parameters for
             :func:`~robot.parsing.parser.parser.get_resource_model` used internally.

        New in Robot Framework 6.1. See also :meth:`from_file_system` and
        :meth:`from_model`.
        """
        from robot.parsing import get_resource_model
        model = get_resource_model(string, data_only=True, **config)
        return cls.from_model(model)

    @classmethod
    def from_model(cls, model: 'File') -> 'ResourceFile':
        """Create a :class:`ResourceFile` object based on the given ``model``.

        :param model: Model to create the suite from.

        The model can be created by using the
        :func:`~robot.parsing.parser.parser.get_resource_model` function and possibly
        modified by other tooling in the :mod:`robot.parsing` module.

        New in Robot Framework 6.1. See also :meth:`from_file_system` and
        :meth:`from_string`.
        """
        from .builder import RobotParser
        return RobotParser().parse_resource_model(model)

    @overload
    def find_keywords(self, name: str, count: Literal[1]) -> 'UserKeyword':
        ...

    @overload
    def find_keywords(self, name: str, count: 'int|None' = None) -> 'list[UserKeyword]':
        ...

    def find_keywords(self, name: str, count: 'int|None' = None) \
            -> 'list[UserKeyword]|UserKeyword':
        return self.keyword_finder.find(name, count)

    def to_dict(self) -> DataDict:
        data = {}
        if self._source:
            data['source'] = str(self._source)
        if self.doc:
            data['doc'] = self.doc
        if self.imports:
            data['imports'] = self.imports.to_dicts()
        if self.variables:
            data['variables'] = self.variables.to_dicts()
        if self.keywords:
            data['keywords'] = self.keywords.to_dicts()
        return data


class UserKeyword(KeywordImplementation):
    """Represents a user keyword."""
    type = KeywordImplementation.USER_KEYWORD
    fixture_class = Keyword
    __slots__ = ['timeout', '_setup', '_teardown']

    def __init__(self, name: str = '',
                 args: 'ArgumentSpec|Sequence[str]|None' = (),
                 doc: str = '',
                 tags: 'Tags|Sequence[str]' = (),
                 timeout: 'str|None' = None,
                 lineno: 'int|None' = None,
                 owner: 'ResourceFile|None' = None,
                 parent: 'BodyItemParent|None' = None,
                 error: 'str|None' = None):
        super().__init__(name, args, doc, tags, lineno, owner, parent, error)
        self.timeout = timeout
        self._setup = None
        self._teardown = None
        self.body = []

    @setter
    def args(self, spec: 'ArgumentSpec|Sequence[str]|None') -> ArgumentSpec:
        if not spec:
            spec = ArgumentSpec()
        elif not isinstance(spec, ArgumentSpec):
            spec = UserKeywordArgumentParser().parse(spec)
        spec.name = lambda: self.full_name
        return spec

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        return Body(self, body)

    @property
    def setup(self) -> Keyword:
        """User keyword setup as a :class:`Keyword` object.

        New in Robot Framework 7.0.
        """
        if self._setup is None:
            self.setup = None
        return self._setup

    @setup.setter
    def setup(self, setup: 'Keyword|DataDict|None'):
        self._setup = create_fixture(self.fixture_class, setup, self, Keyword.SETUP)

    @property
    def has_setup(self) -> bool:
        """Check does a keyword have a setup without creating a setup object.

        See :attr:`has_teardown` for more information. New in Robot Framework 7.0.
        """
        return bool(self._setup)

    @property
    def teardown(self) -> Keyword:
        """User keyword teardown as a :class:`Keyword` object."""
        if self._teardown is None:
            self.teardown = None
        return self._teardown

    @teardown.setter
    def teardown(self, teardown: 'Keyword|DataDict|None'):
        self._teardown = create_fixture(self.fixture_class, teardown, self, Keyword.TEARDOWN)

    @property
    def has_teardown(self) -> bool:
        """Check does a keyword have a teardown without creating a teardown object.

        A difference between using ``if kw.has_teardown:`` and ``if kw.teardown:``
        is that accessing the :attr:`teardown` attribute creates a :class:`Keyword`
        object representing the teardown even when the user keyword actually does
        not have one. This can have an effect on memory usage.

        New in Robot Framework 6.1.
        """
        return bool(self._teardown)

    def create_runner(self, name: 'str|None',
                      languages: 'LanguagesLike' = None) \
            -> 'UserKeywordRunner|EmbeddedArgumentsRunner':
        if self.embedded:
            return EmbeddedArgumentsRunner(self, name)
        return UserKeywordRunner(self)

    def bind(self, data: Keyword) -> 'UserKeyword':
        kw = UserKeyword('', self.args.copy(), self.doc, self.tags, self.timeout,
                         self.lineno, self.owner, data.parent, self.error)
        # Avoid possible errors setting name with invalid embedded args.
        kw._name = self._name
        kw.embedded = self.embedded
        if self.has_setup:
            kw.setup = self.setup.to_dict()
        if self.has_teardown:
            kw.teardown = self.teardown.to_dict()
        kw.body = self.body.to_dicts()
        return kw

    def to_dict(self) -> DataDict:
        data: DataDict = {'name': self.name}
        for name, value in [('args', tuple(self._decorate_arg(a) for a in self.args)),
                            ('doc', self.doc),
                            ('tags', tuple(self.tags)),
                            ('timeout', self.timeout),
                            ('lineno', self.lineno),
                            ('error', self.error)]:
            if value:
                data[name] = value
        if self.has_setup:
            data['setup'] = self.setup.to_dict()
        data['body'] = self.body.to_dicts()
        if self.has_teardown:
            data['teardown'] = self.teardown.to_dict()
        return data

    def _decorate_arg(self, arg: ArgInfo) -> str:
        if arg.kind == arg.VAR_NAMED:
            deco = '&'
        elif arg.kind in (arg.VAR_POSITIONAL, arg.NAMED_ONLY_MARKER):
            deco = '@'
        else:
            deco = '$'
        result = f'{deco}{{{arg.name}}}'
        if arg.default is not NOT_SET:
            result += f'={arg.default}'
        return result


class Variable(ModelObject):
    repr_args = ('name', 'value', 'separator')

    def __init__(self, name: str = '',
                 value: Sequence[str] = (),
                 separator: 'str|None' = None,
                 owner: 'ResourceFile|None' = None,
                 lineno: 'int|None' = None,
                 error: 'str|None' = None):
        self.name = name
        self.value = tuple(value)
        self.separator = separator
        self.owner = owner
        self.lineno = lineno
        self.error = error

    @property
    def source(self) -> 'Path|None':
        return self.owner.source if self.owner is not None else None

    def report_error(self, message: str, level: str = 'ERROR'):
        source = self.source or '<unknown>'
        line = f' on line {self.lineno}' if self.lineno else ''
        LOGGER.write(f"Error in file '{source}'{line}: "
                     f"Setting variable '{self.name}' failed: {message}", level)

    def to_dict(self) -> DataDict:
        data = {'name': self.name, 'value': self.value}
        if self.lineno:
            data['lineno'] = self.lineno
        if self.error:
            data['error'] = self.error
        return data

    def _include_in_repr(self, name: str, value: Any) -> bool:
        return not (name == 'separator' and value is None)


class Import(ModelObject):
    """Represents library, resource file or variable file import."""
    repr_args = ('type', 'name', 'args', 'alias')
    LIBRARY = 'LIBRARY'
    RESOURCE = 'RESOURCE'
    VARIABLES = 'VARIABLES'

    def __init__(self, type: Literal['LIBRARY', 'RESOURCE', 'VARIABLES'],
                 name: str,
                 args: Sequence[str] = (),
                 alias: 'str|None' = None,
                 owner: 'ResourceFile|None' = None,
                 lineno: 'int|None' = None):
        if type not in (self.LIBRARY, self.RESOURCE, self.VARIABLES):
            raise ValueError(f"Invalid import type: Expected '{self.LIBRARY}', "
                             f"'{self.RESOURCE}' or '{self.VARIABLES}', got '{type}'.")
        self.type = type
        self.name = name
        self.args = tuple(args)
        self.alias = alias
        self.owner = owner
        self.lineno = lineno

    @property
    def source(self) -> 'Path|None':
        return self.owner.source if self.owner is not None else None

    @property
    def directory(self) -> 'Path|None':
        source = self.source
        return source.parent if source and not source.is_dir() else source

    @property
    def setting_name(self) -> str:
        return self.type.title()

    def select(self, library: Any, resource: Any, variables: Any) -> Any:
        return {self.LIBRARY: library,
                self.RESOURCE: resource,
                self.VARIABLES: variables}[self.type]

    def report_error(self, message: str, level: str = 'ERROR'):
        source = self.source or '<unknown>'
        line = f' on line {self.lineno}' if self.lineno else ''
        LOGGER.write(f"Error in file '{source}'{line}: {message}", level)

    @classmethod
    def from_dict(cls, data) -> 'Import':
        return cls(**data)

    def to_dict(self) -> DataDict:
        data: DataDict = {'type': self.type, 'name': self.name}
        if self.args:
            data['args'] = self.args
        if self.alias:
            data['alias'] = self.alias
        if self.lineno:
            data['lineno'] = self.lineno
        return data

    def _include_in_repr(self, name: str, value: Any) -> bool:
        return name in ('type', 'name') or value


class Imports(model.ItemList):

    def __init__(self, owner: ResourceFile, imports: Sequence[Import] = ()):
        super().__init__(Import, {'owner': owner}, items=imports)

    def library(self, name: str, args: Sequence[str] = (), alias: 'str|None' = None,
                lineno: 'int|None' = None) -> Import:
        """Create library import."""
        return self.create(Import.LIBRARY, name, args, alias, lineno=lineno)

    def resource(self, name: str, lineno: 'int|None' = None) -> Import:
        """Create resource import."""
        return self.create(Import.RESOURCE, name, lineno=lineno)

    def variables(self, name: str, args: Sequence[str] = (),
                  lineno: 'int|None' = None) -> Import:
        """Create variables import."""
        return self.create(Import.VARIABLES, name, args, lineno=lineno)

    def create(self, *args, **kwargs) -> Import:
        """Generic method for creating imports.

        Import type specific methods :meth:`library`, :meth:`resource` and
        :meth:`variables` are recommended over this method.
        """
        # RF 6.1 changed types to upper case. Code below adds backwards compatibility.
        if args:
            args = (args[0].upper(),) + args[1:]
        elif 'type' in kwargs:
            kwargs['type'] = kwargs['type'].upper()
        return super().create(*args, **kwargs)


class Variables(model.ItemList[Variable]):

    def __init__(self, owner: ResourceFile, variables: Sequence[Variable] = ()):
        super().__init__(Variable, {'owner': owner}, items=variables)


class UserKeywords(model.ItemList[UserKeyword]):

    def __init__(self, owner: ResourceFile, keywords: Sequence[UserKeyword] = ()):
        self.invalidate_keyword_cache = owner.keyword_finder.invalidate_cache
        self.invalidate_keyword_cache()
        super().__init__(UserKeyword, {'owner': owner}, items=keywords)

    def append(self, item: 'UserKeyword|DataDict') -> UserKeyword:
        self.invalidate_keyword_cache()
        return super().append(item)

    def extend(self, items: 'Iterable[UserKeyword|DataDict]'):
        self.invalidate_keyword_cache()
        return super().extend(items)

    def __setitem__(self, index: 'int|slice', item: 'Iterable[UserKeyword|DataDict]'):
        self.invalidate_keyword_cache()
        return super().__setitem__(index, item)

    def insert(self, index: int, item: 'UserKeyword|DataDict'):
        self.invalidate_keyword_cache()
        super().insert(index, item)

    def clear(self):
        self.invalidate_keyword_cache()
        super().clear()
