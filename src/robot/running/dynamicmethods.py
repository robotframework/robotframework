#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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
from robot.utils import get_error_message, unic


def no_dynamic_method(*args):
    pass


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

    def __call__(self, *args):
        try:
            return self._handle_return_value(self.method(*args))
        except:
            raise DataError("Calling dynamic method '%s' failed: %s"
                            % (self.method.__name__, get_error_message()))

    def _handle_return_value(self, value):
        raise NotImplementedError

    def _to_string(self, value):
        if not isinstance(value, basestring):
            raise DataError('Return value must be string.')
        return value if isinstance(value, unicode) else unic(value, 'UTF-8')

    def _to_list_of_strings(self, value):
        try:
            return [self._to_string(v) for v in value]
        except (TypeError, DataError):
            raise DataError('Return value must be list of strings.')

    def __nonzero__(self):
        return self.method is not no_dynamic_method


class GetKeywordNames(_DynamicMethod):
    _underscore_name = 'get_keyword_names'

    def _handle_return_value(self, value):
        return self._to_list_of_strings(value or [])


class RunKeyword(_DynamicMethod):
    _underscore_name = 'run_keyword'


class GetKeywordDocumentation(_DynamicMethod):
    _underscore_name = 'get_keyword_documentation'

    def _handle_return_value(self, value):
        return self._to_string(value or '')


class GetKeywordArguments(_DynamicMethod):
    _underscore_name = 'get_keyword_arguments'

    def _handle_return_value(self, value):
        if value is None:
            return ['*unknown']
        return self._to_list_of_strings(value)
