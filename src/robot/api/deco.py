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


def not_keyword(func):
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


@not_keyword
def keyword(name=None, tags=(), types=()):
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
        return keyword()(name)

    def decorator(func):
        func.robot_name = name
        func.robot_tags = tags
        func.robot_types = types
        return func

    return decorator


@not_keyword
def library(scope=None, version=None, converters=None, doc_format=None, listener=None,
            auto_keywords=False):
    """Class decorator to control keyword discovery and other library settings.

    By default disables automatic keyword detection by setting class attribute
    ``ROBOT_AUTO_KEYWORDS = False`` to the decorated library. In that mode
    only methods decorated explicitly with the :func:`keyword` decorator become
    keywords. If that is not desired, automatic keyword discovery can be
    enabled by using ``auto_keywords=True``.

    Arguments ``scope``, ``version``, ``converters``, ``doc_format`` and ``listener``
    set library's scope, version, converters, documentation format and listener by
    using class attributes ``ROBOT_LIBRARY_SCOPE``, ``ROBOT_LIBRARY_VERSION``,
    ``ROBOT_LIBRARY_CONVERTERS``, ``ROBOT_LIBRARY_DOC_FORMAT`` and
    ``ROBOT_LIBRARY_LISTENER``, respectively. These attributes are only set if
    the related arguments are given and they override possible existing attributes
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
    if inspect.isclass(scope):
        return library()(scope)

    def decorator(cls):
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
