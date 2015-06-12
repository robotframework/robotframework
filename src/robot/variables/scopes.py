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

from robot.errors import DataError

from .variables import Variables


GLOBAL_VARIABLES = Variables()


class VariableScopes(object):

    def __init__(self):
        variables = GLOBAL_VARIABLES.copy()
        self._suite = self.current = variables
        self._test = None
        self._uk_handlers = []    # FIXME: Better name
        self._set_test_vars = Variables()
        self._set_kw_vars = Variables()
        self._set_global_vars = Variables()

    def __len__(self):
        return len(self.current)

    def replace_list(self, items, replace_until=None):
        return self.current.replace_list(items, replace_until)

    def replace_scalar(self, items):
        return self.current.replace_scalar(items)

    def replace_string(self, string, ignore_errors=False):
        return self.current.replace_string(string, ignore_errors=ignore_errors)

    def set_from_file(self, path, args, overwrite=False):
        variables = self._suite.set_from_file(path, args, overwrite)
        if self._test is not None:
            self._test.set_from_file(variables, overwrite=True)
        for varz, _ in self._uk_handlers:
            varz.set_from_file(variables, overwrite=True)
        if self._uk_handlers:
            self.current.set_from_file(variables, overwrite=True)

    def set_from_variable_table(self, rawvariables, overwrite=False):
        self._suite.set_from_variable_table(rawvariables, overwrite)
        if self._test is not None:
            self._test.set_from_variable_table(rawvariables, overwrite)
        for varz, _ in self._uk_handlers:
            varz.set_from_variable_table(rawvariables, overwrite)
        if self._uk_handlers:
            self.current.set_from_variable_table(rawvariables, overwrite)

    def resolve_delayed(self):
        self.current.resolve_delayed()

    def __getitem__(self, name):
        return self.current[name]

    def __setitem__(self, name, value):
        self.current[name] = value

    def end_suite(self):
        self._suite = self._test = self.current = None

    def start_test(self):
        self._test = self.current = self._suite.copy()

    def end_test(self):
        self.current = self._suite
        self._set_test_vars.clear()

    def start_uk(self):
        self._uk_handlers.append((self.current, self._set_kw_vars))
        self.current = self._suite.copy()
        self.current.update(self._set_test_vars)
        self.current.update(self._set_kw_vars)
        self._set_kw_vars = self._set_kw_vars.copy()

    def end_uk(self):
        self.current, self._set_kw_vars = self._uk_handlers.pop()

    def set_global(self, name, value):
        name, value = self._set_global_suite_or_test(GLOBAL_VARIABLES, name, value)
        # TODO: This needs to be implemented otherwise...
        from robot.running import EXECUTION_CONTEXTS
        for ns in EXECUTION_CONTEXTS.namespaces:
            ns.variables.set_suite(name, value)

    def set_suite(self, name, value):
        name, value = self._set_global_suite_or_test(self._suite, name, value)
        self.set_test(name, value, False)

    def set_test(self, name, value, fail_if_no_test=True):
        if self._test is not None:
            name, value = self._set_global_suite_or_test(self._test, name, value)
        elif fail_if_no_test:
            raise DataError("Cannot set test variable when no test is started")
        for varz, _ in self._uk_handlers:
            varz[name] = value
        self.current[name] = value
        self._set_test_vars[name] = value

    def set_keyword(self, name, value):
        self.current[name] = value
        self._set_kw_vars[name] = value

    def _set_global_suite_or_test(self, variables, name, value):
        variables[name] = value
        # Avoid creating new list/dict objects in different scopes.
        if name[0] != '$':
            name = '$' + name[1:]
            value = variables[name]
        return name, value

    def __iter__(self):
        return iter(self.current)

    @property
    def store(self):
        return self.current.store
