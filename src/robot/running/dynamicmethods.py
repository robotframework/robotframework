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
from robot.utils import (get_error_message, is_java_method, is_bytes,
                         is_list_like, is_unicode, type_name, py2to3)

from .arguments import JavaArgumentParser, PythonArgumentParser


def no_dynamic_method(*args):
    return None


@py2to3
class _DynamicMethod(object):
    _underscore_name = NotImplemented

    def __init__(self, lib):
        self.method = self._get_method(lib)

    def _get_method(self, lib):
        for name in self._underscore_name, self._camelCaseName:
            method = getattr(lib, name, None)
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

    def __call__(self, *args):
        try:
            return self._handle_return_value(self.method(*args))
        except:
            raise DataError("Calling dynamic method '%s' failed: %s"
                            % (self.name, get_error_message()))

    def _handle_return_value(self, value):
        raise NotImplementedError

    def _to_string(self, value, allow_tuple=False, allow_none=False):
        if is_unicode(value):
            return value
        if is_bytes(value):
            return value.decode('UTF-8')
        if allow_tuple and is_list_like(value) and len(value) > 0:
            return tuple(value)
        if allow_none and value is None:
            return value
        or_tuple = ' or a non-empty tuple' if allow_tuple else ''
        raise DataError('Return value must be a string%s, got %s.'
                        % (or_tuple, type_name(value)))

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
            raise DataError('Return value must be a list of strings%s.'
                            % (' or non-empty tuples' if allow_tuples else ''))

    def __nonzero__(self):
        return self.method is not no_dynamic_method


class GetKeywordNames(_DynamicMethod):
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


class RunKeyword(_DynamicMethod):
    _underscore_name = 'run_keyword'

    @property
    def supports_kwargs(self):
        if is_java_method(self.method):
            return self._supports_java_kwargs(self.method)
        return self._supports_python_kwargs(self.method)

    def _supports_python_kwargs(self, method):
        spec = PythonArgumentParser().parse(method)
        return len(spec.positional) == 3

    def _supports_java_kwargs(self, method):
        func = self.method.im_func if hasattr(method, 'im_func') else method
        signatures = func.argslist[:func.nargs]
        spec = JavaArgumentParser().parse(signatures)
        return (self._java_single_signature_kwargs(spec) or
                self._java_multi_signature_kwargs(spec))

    def _java_single_signature_kwargs(self, spec):
        return len(spec.positional) == 1 and spec.varargs and spec.kwargs

    def _java_multi_signature_kwargs(self, spec):
        return len(spec.positional) == 3 and not (spec.varargs or spec.kwargs)


class GetKeywordDocumentation(_DynamicMethod):
    _underscore_name = 'get_keyword_documentation'

    def _handle_return_value(self, value):
        return self._to_string(value or '')


class GetKeywordArguments(_DynamicMethod):
    _underscore_name = 'get_keyword_arguments'

    def __init__(self, lib):
        _DynamicMethod.__init__(self, lib)
        self._supports_kwargs = RunKeyword(lib).supports_kwargs

    def _handle_return_value(self, value):
        if value is None:
            if self._supports_kwargs:
                return ['*varargs', '**kwargs']
            return ['*varargs']
        return self._to_list_of_strings(value, allow_tuples=True)


class GetKeywordTypes(_DynamicMethod):
    _underscore_name = 'get_keyword_types'

    def _handle_return_value(self, value):
        return value if self else {}


class GetKeywordTags(_DynamicMethod):
    _underscore_name = 'get_keyword_tags'

    def _handle_return_value(self, value):
        return self._to_list_of_strings(value)


class GetKeywordSource(_DynamicMethod):
    _underscore_name = 'get_keyword_source'

    def _handle_return_value(self, value):
        return self._to_string(value, allow_none=True)
