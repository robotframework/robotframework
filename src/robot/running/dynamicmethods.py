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

from robot.errors import DataError
from robot.utils import get_error_message, is_list_like, type_name

from .arguments import PythonArgumentParser
from .context import EXECUTION_CONTEXTS


def no_dynamic_method(*args):
    return None


class DynamicMethod:
    _underscore_name = NotImplemented

    def __init__(self, instance):
        self.instance = instance
        self.method = self._get_method(instance)

    def _get_method(self, instance):
        for name in self._underscore_name, self._camelCaseName:
            method = getattr(instance, name, None)
            if callable(method):
                return method
        return no_dynamic_method

    @property
    def _camelCaseName(self):
        tokens = self._underscore_name.split('_')
        return ''.join([tokens[0]] + [t.capitalize() for t in tokens[1:]])

    @property
    def name(self):
        return self.method.__name__

    def __call__(self, *args, **kwargs):
        try:
            ctx = EXECUTION_CONTEXTS.current
            result = self.method(*args, **kwargs)
            if ctx and ctx.asynchronous.is_loop_required(result):
                result = ctx.asynchronous.run_until_complete(result)
            return self._handle_return_value(result)
        except Exception:
            raise DataError(f"Calling dynamic method '{self.name}' failed: "
                            f"{get_error_message()}")

    def _handle_return_value(self, value):
        raise NotImplementedError

    def _to_string(self, value, allow_tuple=False, allow_none=False):
        if isinstance(value, str):
            return value
        if isinstance(value, bytes):
            return value.decode('UTF-8')
        if allow_tuple and is_list_like(value) and len(value) > 0:
            return tuple(value)
        if allow_none and value is None:
            return value
        allowed = 'a string or a non-empty tuple' if allow_tuple else 'a string'
        raise DataError(f'Return value must be {allowed}, got {type_name(value)}.')

    def _to_list(self, value):
        if value is None:
            return ()
        if not is_list_like(value):
            raise DataError
        return value

    def _to_list_of_strings(self, value, allow_tuples=False):
        try:
            return [self._to_string(item, allow_tuples)
                    for item in self._to_list(value)]
        except DataError:
            allowed = 'strings or non-empty tuples' if allow_tuples else 'strings'
            raise DataError(f'Return value must be a list of {allowed}, '
                            f'got {type_name(value)}.')

    def __bool__(self):
        return self.method is not no_dynamic_method


class GetKeywordNames(DynamicMethod):
    _underscore_name = 'get_keyword_names'

    def _handle_return_value(self, value):
        names = self._to_list_of_strings(value)
        return list(self._remove_duplicates(names))

    def _remove_duplicates(self, names):
        seen = set()
        for name in names:
            if name not in seen:
                seen.add(name)
                yield name


class RunKeyword(DynamicMethod):
    _underscore_name = 'run_keyword'

    def __init__(self, instance, keyword_name: 'str|None' = None,
                 supports_named_args: 'bool|None' = None):
        super().__init__(instance)
        self.keyword_name = keyword_name
        self._supports_named_args = supports_named_args

    @property
    def supports_named_args(self) -> bool:
        if self._supports_named_args is None:
            spec = PythonArgumentParser().parse(self.method)
            self._supports_named_args = len(spec.positional) == 3
        return self._supports_named_args

    def __call__(self, *positional, **named):
        if self.supports_named_args:
            args = (self.keyword_name, positional, named)
        elif named:
            # This should never happen.
            raise ValueError(f"'named' should not be used when named-argument "
                             f"support is not enabled, got {named}.")
        else:
            args = (self.keyword_name, positional)
        return self.method(*args)


class GetKeywordDocumentation(DynamicMethod):
    _underscore_name = 'get_keyword_documentation'

    def _handle_return_value(self, value):
        return self._to_string(value or '')


class GetKeywordArguments(DynamicMethod):
    _underscore_name = 'get_keyword_arguments'

    def __init__(self, instance, supports_named_args: 'bool|None' = None):
        super().__init__(instance)
        if supports_named_args is None:
            self.supports_named_args = RunKeyword(instance).supports_named_args
        else:
            self.supports_named_args = supports_named_args

    def _handle_return_value(self, value):
        if value is None:
            if self.supports_named_args:
                return ['*varargs', '**kwargs']
            return ['*varargs']
        return self._to_list_of_strings(value, allow_tuples=True)


class GetKeywordTypes(DynamicMethod):
    _underscore_name = 'get_keyword_types'

    def _handle_return_value(self, value):
        return value if self else {}


class GetKeywordTags(DynamicMethod):
    _underscore_name = 'get_keyword_tags'

    def _handle_return_value(self, value):
        return self._to_list_of_strings(value)


class GetKeywordSource(DynamicMethod):
    _underscore_name = 'get_keyword_source'

    def _handle_return_value(self, value):
        return self._to_string(value, allow_none=True)
