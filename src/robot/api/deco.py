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

import inspect

from typing import overload, cast, Callable, TypeVar, Union, List, Any, TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    from typing_extensions import Literal

Fn = TypeVar("Fn", bound=Callable[..., Any])
Cls = TypeVar("Cls", bound=type)
_Types = Union[Mapping[str, type], List[type], None]


def not_keyword(func: Fn) -> Fn:
    """Decorator to disable exposing functions or methods as keywords.

    Examples::

        @not_keyword
        def not_exposed_as_keyword():
            # ...

        def exposed_as_keyword():
            # ...

    Alternatively the automatic keyword discovery can be disabled with
    the :func:`library` decorator or by setting the ``ROBOT_AUTO_KEYWORDS``
    attribute to a false value.

    New in Robot Framework 3.2.
    """
    func.robot_not_keyword = True  # type: ignore[attr-defined]
    return func


not_keyword.robot_not_keyword = True  # type: ignore[attr-defined]


@overload
def keyword(name: Fn) -> Fn: ...


@overload
def keyword(name: str = None, tags: List[str] = ..., types: _Types = ...) -> Callable[[Fn], Fn]: ...


@not_keyword
def keyword(name: object = None, tags: object = (), types: object = ()) -> object:
    """Decorator to set custom name, tags and argument types to keywords.

    This decorator creates ``robot_name``, ``robot_tags`` and ``robot_types``
    attributes on the decorated keyword function or method based on the
    provided arguments. Robot Framework checks them to determine the keyword's
    name, tags, and argument types, respectively.

    Name must be given as a string, tags as a list of strings, and types
    either as a dictionary mapping argument names to types or as a list
    of types mapped to arguments based on position. It is OK to specify types
    only to some arguments, and setting ``types`` to ``None`` disables type
    conversion altogether.

    If the automatic keyword discovery has been disabled with the
    :func:`library` decorator or by setting the ``ROBOT_AUTO_KEYWORDS``
    attribute to a false value, this decorator is needed to mark functions
    or methods keywords.

    Examples::

        @keyword
        def example():
            # ...

        @keyword('Login as user "${user}" with password "${password}"',
                 tags=['custom name', 'embedded arguments', 'tags'])
        def login(user, password):
            # ...

        @keyword(types={'length': int, 'case_insensitive': bool})
        def types_as_dict(length, case_insensitive):
            # ...

        @keyword(types=[int, bool])
        def types_as_list(length, case_insensitive):
            # ...

        @keyword(types=None])
        def no_conversion(length, case_insensitive=False):
            # ...
    """
    if inspect.isroutine(name):
        return keyword()(name)  # type: ignore[type-var, return-value]

    def decorator(func: Fn) -> Fn:
        func.robot_name = name  # type:ignore[attr-defined]
        func.robot_tags = tags  # type:ignore[attr-defined]
        func.robot_types = types  # type:ignore[attr-defined]
        return func

    return decorator


@overload
def library(scope: Cls) -> Cls: ...


@overload
def library(scope: 'Literal["GLOBAL", "SUITE", "TEST", None]' = None,
            version: str = None, doc_format: str = None, listener: str = None,
            auto_keywords: bool = False) -> Callable[[Cls], Cls]: ...


@not_keyword
def library(scope: object = None, version: str = None, doc_format: str = None, listener: str = None,
            auto_keywords: bool = False) -> object:
    """Class decorator to control keyword discovery and other library settings.

    By default disables automatic keyword detection by setting class attribute
    ``ROBOT_AUTO_KEYWORDS = False`` to the decorated library. In that mode
    only methods decorated explicitly with the :func:`keyword` decorator become
    keywords. If that is not desired, automatic keyword discovery can be
    enabled by using ``auto_keywords=True``.

    Arguments ``scope``, ``version``, ``doc_format`` and ``listener`` set the
    library scope, version, documentation format and listener by using class
    attributes ``ROBOT_LIBRARY_SCOPE``, ``ROBOT_LIBRARY_VERSION``,
    ``ROBOT_LIBRARY_DOC_FORMAT`` and ``ROBOT_LIBRARY_LISTENER``, respectively.
    These attributes are only set if the related arguments are given and they
    override possible existing attributes in the decorated class.

    Examples::

        @library
        class KeywordDiscovery:

            @keyword
            def do_something(self):
                # ...

            def not_keyword(self):
                # ...


        @library(scope='GLOBAL', version='3.2')
        class LibraryConfiguration:
            # ...

    The ``@library`` decorator is new in Robot Framework 3.2.
    """
    if inspect.isclass(scope):
        return library()(cast(type, scope))

    def decorator(cls: Cls) -> Cls:
        if scope is not None:
            cls.ROBOT_LIBRARY_SCOPE = scope  # type:ignore[attr-defined]
        if version is not None:
            cls.ROBOT_LIBRARY_VERSION = version  # type:ignore[attr-defined]
        if doc_format is not None:
            cls.ROBOT_LIBRARY_DOC_FORMAT = doc_format  # type:ignore[attr-defined]
        if listener is not None:
            cls.ROBOT_LIBRARY_LISTENER = listener  # type:ignore[attr-defined]
        cls.ROBOT_AUTO_KEYWORDS = auto_keywords  # type:ignore[attr-defined]
        return cls

    return decorator
