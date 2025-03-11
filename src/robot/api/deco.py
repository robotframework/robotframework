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

import importlib
import multiprocessing as mp
import concurrent.futures
import collections
import robot.errors
from functools import wraps
from enum import Enum
from dataclasses import dataclass
import queue
import robot.api.logger
from typing import Any, Callable, Literal, Sequence, TypeVar, Union, overload

from .interfaces import TypeHints


# Current annotations report `attr-defined` errors. This can be solved once Python 3.10
# becomes the minimum version (error-free conditional typing proved too complex).
# See: https://discuss.python.org/t/questions-related-to-typing-overload-style/38130
F = TypeVar('F', bound=Callable[..., Any])    # Any function.
K = TypeVar('K', bound=Callable[..., Any])    # Keyword function.
L = TypeVar('L', bound=type)                  # Library class.
KeywordDecorator = Callable[[K], K]
LibraryDecorator = Callable[[L], L]
Scope = Literal['GLOBAL', 'SUITE', 'TEST', 'TASK']
Converter = Union[Callable[[Any], Any], Callable[[Any, Any], Any]]
DocFormat = Literal['ROBOT', 'HTML', 'TEXT', 'REST']


class responses(Enum):
    SUCCESS = 1
    EXCEPTION = 2
    LOG = 3

@dataclass
class _subprocess_call:
    name: str
    args: Sequence
    kwargs: dict


@dataclass
class _subprocess_response:
    response_type: responses
    value: Any


def _process_worker_for_decorator(libnameIn, classname,  qToSubprocess, qFromSubprocess):
    infra = importlib.import_module("robot.api.deco")
    infra.run_in_its_own_process_decorator._trunk = False
    logger = importlib.import_module("robot.api.logger")

    for logfunction in ["trace", "debug", "console", "info", "warn", "error", "write"]:
        def _worker(*args, **kwargs):
            qFromSubprocess.put(_subprocess_response(response_type=responses.LOG, value=(logfunction, args, kwargs)))
        setattr(logger, logfunction, _worker)

    m = importlib.import_module(libnameIn)
    if classname:
        m = getattr(m, classname)
    while True:
        try:
            call = qToSubprocess.get()
            result = getattr(m, call.name)(*call.args, **call.kwargs)
            qFromSubprocess.put(_subprocess_response(response_type=responses.SUCCESS, value=result))
        except Exception as e:
            qFromSubprocess.put(_subprocess_response(response_type=responses.EXCEPTION, value=e))


class run_in_its_own_process_decorator:
    _trunk = True
    def __init__(self, module_name, class_name=None, ctx="spawn"):
        self._module_name = module_name
        self._class_name = class_name
        if self._trunk:
            self._ctx = mp.get_context(ctx)
            self._setup()

    def _setup(self):
        self._qToSubprocess = self._ctx.Queue()
        self._qFromSubprocess = self._ctx.Queue()
        self._process = self._ctx.Process(target=_process_worker_for_decorator, 
                                          args=(self._module_name, self._class_name, self._qToSubprocess, self._qFromSubprocess),
                                          daemon=True)
        self._process.start()

    def __call__(self, fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            if self._trunk:
                assert self._process.is_alive(), "Subprocess has died"
                self._qToSubprocess.put(_subprocess_call(fun.__name__, args, kwargs))
                while True:
                    try:
                        response = self._qFromSubprocess.get(timeout=None)
                        if response.response_type ==  responses.SUCCESS:
                            return response.value
                        elif response.response_type == responses.EXCEPTION:
                            raise response.value
                        elif response.response_type == responses.LOG:
                            (method, args, kwargs,) = response.value
                            getattr(robot.api.logger, method)(*args, **kwargs)
                            print((method, args, kwargs,))
                        else:
                            assert False, "Unknown response type"
                    except queue.Empty:
                        pass
                    except robot.errors.TimeoutError:
                        self._process.terminate()
                        self._process.join()
                        self._qToSubprocess.close()
                        self._qFromSubprocess.close()
                        self._setup()
                        raise
            else:
                return fun(*args, **kwargs)
        return wrapper

def not_keyword(func: F) -> F:
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
    func.robot_not_keyword = True
    return func


not_keyword.robot_not_keyword = True


@overload
def keyword(func: K, /) -> K:
    ...


@overload
def keyword(name: 'str | None' = None,
            tags: Sequence[str] = (),
            types: 'TypeHints | None' = ()) -> KeywordDecorator:
    ...


@not_keyword
def keyword(name: 'K | str | None' = None,
            tags: Sequence[str] = (),
            types: 'TypeHints | None' = ()) -> 'K | KeywordDecorator':
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

        @keyword(types=None)
        def no_conversion(length, case_insensitive=False):
            # ...
    """
    if callable(name):
        return keyword()(name)

    def decorator(func: F) -> F:
        func.robot_name = name
        func.robot_tags = tags
        func.robot_types = types
        return func

    return decorator


@overload
def library(cls: L, /) -> L:
    ...


@overload
def library(scope: 'Scope | None' = None,
            version: 'str | None' = None,
            converters: 'dict[type, Converter] | None' = None,
            doc_format: 'DocFormat | None' = None,
            listener: 'Any | None' = None,
            auto_keywords: bool = False) -> LibraryDecorator:
    ...


@not_keyword
def library(scope: 'L | Scope | None' = None,
            version: 'str | None' = None,
            converters: 'dict[type, Converter] | None' = None,
            doc_format: 'DocFormat | None' = None,
            listener: 'Any | None' = None,
            auto_keywords: bool = False) -> 'L | LibraryDecorator':
    """Class decorator to control keyword discovery and other library settings.

    Disables automatic keyword detection by setting class attribute
    ``ROBOT_AUTO_KEYWORDS = False`` to the decorated library by default. In that
    mode only methods decorated explicitly with the :func:`keyword` decorator
    become keywords. If that is not desired, automatic keyword discovery can be
    enabled by using ``auto_keywords=True``.

    Arguments ``scope``, ``version``, ``converters``, ``doc_format`` and ``listener``
    set library's scope, version, converters, documentation format and listener by
    using class attributes ``ROBOT_LIBRARY_SCOPE``, ``ROBOT_LIBRARY_VERSION``,
    ``ROBOT_LIBRARY_CONVERTERS``, ``ROBOT_LIBRARY_DOC_FORMAT`` and
    ``ROBOT_LIBRARY_LISTENER``, respectively. These attributes are only set if
    the related arguments are given, and they override possible existing attributes
    in the decorated class.

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
    The ``converters`` argument is new in Robot Framework 5.0.
    """
    if isinstance(scope, type):
        return library()(scope)

    def decorator(cls: L) -> L:
        if scope is not None:
            cls.ROBOT_LIBRARY_SCOPE = scope
        if version is not None:
            cls.ROBOT_LIBRARY_VERSION = version
        if converters is not None:
            cls.ROBOT_LIBRARY_CONVERTERS = converters
        if doc_format is not None:
            cls.ROBOT_LIBRARY_DOC_FORMAT = doc_format
        if listener is not None:
            cls.ROBOT_LIBRARY_LISTENER = listener
        cls.ROBOT_AUTO_KEYWORDS = auto_keywords
        return cls

    return decorator
