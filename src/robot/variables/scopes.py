#  Copyright 2008-2015 Nokia Solutions and Networks
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

import os
import tempfile

from robot.errors import DataError
from robot.output import LOGGER
from robot.utils import abspath, find_file, get_error_details, NormalizedDict

from .variables import Variables


GLOBAL_VARIABLES = Variables()


class VariableScopes(object):

    def __init__(self, settings):
        self._global = GlobalVariables(settings)
        GLOBAL_VARIABLES.update(self._global)
        self._suite = None
        self._test = None
        self._scopes = [self._global]
        self._variables_set = SetVariables()

    @property
    def current(self):
        return self._scopes[-1]

    @property
    def _all_scopes(self):
        return reversed(self._scopes)

    @property
    def _scopes_until_suite(self):
        for scope in self._all_scopes:
            yield scope
            if scope is self._suite:
                break

    @property
    def _scopes_until_test(self):
        for scope in self._scopes_until_suite:
            yield scope
            if scope is self._test:
                break

    def start_suite(self):
        self._suite = self._global.copy()
        self._scopes.append(self._suite)

    def end_suite(self):
        self._scopes.pop()
        self._suite = self._scopes[-1] if len(self._scopes) > 1 else None

    def start_test(self):
        self._test = self._suite.copy()
        self._scopes.append(self._test)

    def end_test(self):
        self._scopes.pop()
        self._test = None
        self._variables_set.end_test()

    def start_keyword(self):
        kw = self._suite.copy()
        self._variables_set.start_keyword()
        self._variables_set.update_keyword(kw)
        self._scopes.append(kw)

    def end_keyword(self):
        self._scopes.pop()
        self._variables_set.end_keyword()

    def __getitem__(self, name):
        return self.current[name]

    def __setitem__(self, name, value):
        self.current[name] = value

    def __contains__(self, name):
        return name in self.current

    def replace_list(self, items, replace_until=None):
        return self.current.replace_list(items, replace_until)

    def replace_scalar(self, items):
        return self.current.replace_scalar(items)

    def replace_string(self, string, ignore_errors=False):
        return self.current.replace_string(string, ignore_errors=ignore_errors)

    def set_from_file(self, path, args, overwrite=False):
        variables = None
        for scope in self._scopes_until_suite:
            if variables is None:
                variables = scope.set_from_file(path, args, overwrite)
            else:
                scope.set_from_file(variables, overwrite=overwrite)

    def set_from_variable_table(self, variables, overwrite=False):
        for scope in self._scopes_until_suite:
            scope.set_from_variable_table(variables, overwrite)

    def resolve_delayed(self):
        for scope in self._scopes_until_suite:
            scope.resolve_delayed()

    def set_global(self, name, value):
        for scope in self._all_scopes:
            name, value = self._set_global_suite_or_test(scope, name, value)

    def _set_global_suite_or_test(self, scope, name, value):
        scope[name] = value
        # Avoid creating new list/dict objects in different scopes.
        if name[0] != '$':
            name = '$' + name[1:]
            value = scope[name]
        return name, value

    def set_suite(self, name, value, top=False):
        if top:
            self._scopes[1][name] = value
        else:
            for scope in self._scopes_until_suite:
                name, value = self._set_global_suite_or_test(scope, name, value)

    def set_test(self, name, value):
        if self._test is None:
            raise DataError('Cannot set test variable when no test is started.')
        for scope in self._scopes_until_test:
            name, value = self._set_global_suite_or_test(scope, name, value)
        self._variables_set.set_test(name, value)

    def set_keyword(self, name, value):
        self.current[name] = value
        self._variables_set.set_keyword(name, value)

    def as_dict(self):
        return self.current.as_dict()


class GlobalVariables(Variables):

    def __init__(self, settings):
        Variables.__init__(self)
        self._set_cli_variables(settings)
        self._set_built_in_variables(settings)

    def _set_cli_variables(self, settings):
        for path, args in settings.variable_files:
            try:
                path = find_file(path, file_type='Variable file')
                self.set_from_file(path, args)
            except:
                msg, details = get_error_details()
                LOGGER.error(msg)
                LOGGER.info(details)
        for varstr in settings.variables:
            try:
                name, value = varstr.split(':', 1)
            except ValueError:
                name, value = varstr, ''
            self['${%s}' % name] = value

    def _set_built_in_variables(self, settings):
        for name, value in [('${TEMPDIR}', abspath(tempfile.gettempdir())),
                            ('${EXECDIR}', abspath('.')),
                            ('${/}', os.sep),
                            ('${:}', os.pathsep),
                            ('${\\n}', os.linesep),
                            ('${SPACE}', ' '),
                            ('${True}', True),
                            ('${False}', False),
                            ('${None}', None),
                            ('${null}', None),
                            ('${OUTPUT_DIR}', settings.output_directory),
                            ('${OUTPUT_FILE}', settings.output or 'NONE'),
                            ('${REPORT_FILE}', settings.report or 'NONE'),
                            ('${LOG_FILE}', settings.log or 'NONE'),
                            ('${DEBUG_FILE}', settings.debug_file or 'NONE'),
                            ('${LOG_LEVEL}', settings.log_level),
                            ('${PREV_TEST_NAME}', ''),
                            ('${PREV_TEST_STATUS}', ''),
                            ('${PREV_TEST_MESSAGE}', '')]:
            self[name] = value


class SetVariables(object):

    def __init__(self):
        self._test = NormalizedDict(ignore='_')
        self._scopes = [self._test]

    def end_test(self):
        self._test.clear()

    def start_keyword(self):
        self._scopes.append(self._scopes[-1].copy())

    def end_keyword(self):
        self._scopes.pop()

    def set_test(self, name, value):
        for scope in self._scopes:
            scope[name] = value

    def set_keyword(self, name, value):
        self._scopes[-1][name] = value

    def update_keyword(self, kw):
        for name, value in self._scopes[-1].items():
            kw[name] = value
