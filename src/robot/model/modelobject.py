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

import copy
import json
from pathlib import Path
from typing import Any, Dict, overload, TextIO, Type, TypeVar

from robot.errors import DataError
from robot.utils import get_error_message, SetterAwareType, type_name


T = TypeVar('T', bound='ModelObject')
DataDict = Dict[str, Any]


class ModelObject(metaclass=SetterAwareType):
    repr_args = ()
    __slots__ = []

    @classmethod
    def from_dict(cls: Type[T], data: DataDict) -> T:
        """Create this object based on data in a dictionary.

        Data can be got from the :meth:`to_dict` method or created externally.
        """
        try:
            return cls().config(**data)
        except (AttributeError, TypeError) as err:
            raise DataError(f"Creating '{full_name(cls)}' object from dictionary "
                            f"failed: {err}")

    @classmethod
    def from_json(cls: Type[T], source: 'str|bytes|TextIO|Path') -> T:
        """Create this object based on JSON data.

        The data is given as the ``source`` parameter. It can be:

        - a string (or bytes) containing the data directly,
        - an open file object where to read the data, or
        - a path (``pathlib.Path`` or string) to a UTF-8 encoded file to read.

        The JSON data is first converted to a Python dictionary and the object
        created using the :meth:`from_dict` method.

        Notice that the ``source`` is considered to be JSON data if it is
        a string and contains ``{``. If you need to use ``{`` in a file system
        path, pass it in as a ``pathlib.Path`` instance.
        """
        try:
            data = JsonLoader().load(source)
        except (TypeError, ValueError) as err:
            raise DataError(f'Loading JSON data failed: {err}')
        return cls.from_dict(data)

    def to_dict(self) -> DataDict:
        """Serialize this object into a dictionary.

        The object can be later restored by using the :meth:`from_dict` method.
        """
        raise NotImplementedError

    @overload
    def to_json(self, file: None = None, *, ensure_ascii: bool = False,
                indent: int = 0, separators: 'tuple[str, str]' = (',', ':')) -> str:
        ...

    @overload
    def to_json(self, file: 'TextIO|Path|str', *, ensure_ascii: bool = False,
                indent: int = 0, separators: 'tuple[str, str]' = (',', ':')) -> None:
        ...

    def to_json(self, file: 'None|TextIO|Path|str' = None, *,
                ensure_ascii: bool = False, indent: int = 0,
                separators: 'tuple[str, str]' = (',', ':')) -> 'None|str':
        """Serialize this object into JSON.

        The object is first converted to a Python dictionary using the
        :meth:`to_dict` method and then the dictionary is converted to JSON.

        The ``file`` parameter controls what to do with the resulting JSON data.
        It can be:

        - ``None`` (default) to return the data as a string,
        - an open file object where to write the data, or
        - a path (``pathlib.Path`` or string) to a file where to write
          the data using UTF-8 encoding.

        JSON formatting can be configured using optional parameters that
        are passed directly to the underlying json__ module. Notice that
        the defaults differ from what ``json`` uses.

        __ https://docs.python.org/3/library/json.html
        """
        return JsonDumper(ensure_ascii=ensure_ascii, indent=indent,
                          separators=separators).dump(self.to_dict(), file)

    def config(self: T, **attributes) -> T:
        """Configure model object with given attributes.

        ``obj.config(name='Example', doc='Something')`` is equivalent to setting
        ``obj.name = 'Example'`` and ``obj.doc = 'Something'``.

        New in Robot Framework 4.0.
        """
        for name, value in attributes.items():
            try:
                orig = getattr(self, name)
            except AttributeError:
                raise AttributeError(f"'{full_name(self)}' object does not have "
                                     f"attribute '{name}'")
            # Preserve tuples. Main motivation is converting lists with `from_json`.
            if isinstance(orig, tuple) and not isinstance(value, tuple):
                try:
                    value = tuple(value)
                except TypeError:
                    raise TypeError(f"'{full_name(self)}' object attribute '{name}' "
                                    f"is 'tuple', got '{type_name(value)}'.")
            try:
                setattr(self, name, value)
            except AttributeError as err:
                # Ignore error setting attribute if the object already has it.
                # Avoids problems with `from_dict` with body items having
                # un-settable `type` attribute that is needed in dict data.
                if value != orig:
                    raise AttributeError(f"Setting attribute '{name}' failed: {err}")
        return self

    def copy(self: T, **attributes) -> T:
        """Return a shallow copy of this object.

        :param attributes: Attributes to be set to the returned copy.
            For example, ``obj.copy(name='New name')``.

        See also :meth:`deepcopy`. The difference between ``copy`` and
        ``deepcopy`` is the same as with the methods having same names in
        the copy__ module.

        __ https://docs.python.org/3/library/copy.html
        """
        return copy.copy(self).config(**attributes)

    def deepcopy(self: T, **attributes) -> T:
        """Return a deep copy of this object.

        :param attributes: Attributes to be set to the returned copy.
            For example, ``obj.deepcopy(name='New name')``.

        See also :meth:`copy`. The difference between ``deepcopy`` and
        ``copy`` is the same as with the methods having same names in
        the copy__ module.

        __ https://docs.python.org/3/library/copy.html
        """
        return copy.deepcopy(self).config(**attributes)

    def __repr__(self) -> str:
        arguments = [(name, getattr(self, name)) for name in self.repr_args]
        args_repr = ', '.join(f'{name}={value!r}' for name, value in arguments
                              if self._include_in_repr(name, value))
        return f"{full_name(self)}({args_repr})"

    def _include_in_repr(self, name: str, value: Any) -> bool:
        return True


def full_name(obj_or_cls):
    cls = type(obj_or_cls) if not isinstance(obj_or_cls, type) else obj_or_cls
    parts = cls.__module__.split('.') + [cls.__name__]
    if len(parts) > 1 and parts[0] == 'robot':
        parts[2:-1] = []
    return '.'.join(parts)


class JsonLoader:

    def load(self, source: 'str|bytes|TextIO|Path') -> DataDict:
        try:
            data = self._load(source)
        except (json.JSONDecodeError, TypeError):
            raise ValueError(f'Invalid JSON data: {get_error_message()}')
        if not isinstance(data, dict):
            raise TypeError(f"Expected dictionary, got {type_name(data)}.")
        return data

    def _load(self, source):
        if self._is_path(source):
            with open(source, encoding='UTF-8') as file:
                return json.load(file)
        if hasattr(source, 'read'):
            return json.load(source)
        return json.loads(source)

    def _is_path(self, source):
        if isinstance(source, Path):
            return True
        if not isinstance(source, str) or '{' in source:
            return False
        try:
            return Path(source).is_file()
        except OSError:    # Can happen on Windows w/ Python < 3.10.
            return False


class JsonDumper:

    def __init__(self, **config):
        self.config = config

    @overload
    def dump(self, data: DataDict, output: None = None) -> str:
        ...

    @overload
    def dump(self, data: DataDict, output: 'TextIO|Path|str') -> None:
        ...

    def dump(self, data: DataDict, output: 'None|TextIO|Path|str' = None) -> 'None|str':
        if not output:
            return json.dumps(data, **self.config)
        elif isinstance(output, (str, Path)):
            with open(output, 'w', encoding='UTF-8') as file:
                json.dump(data, file, **self.config)
        elif hasattr(output, 'write'):
            json.dump(data, output, **self.config)
        else:
            raise TypeError(f"Output should be None, path or open file, "
                            f"got {type_name(output)}.")
