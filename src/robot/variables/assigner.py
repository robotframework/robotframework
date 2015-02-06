#  Copyright 2008-2014 Nokia Solutions and Networks
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

import re

from robot.errors import DataError
from robot.utils import safe_repr, format_assign_message, get_error_message


class VariableAssigner(object):
    _valid_extended_attr = re.compile('^[_a-zA-Z]\w*$')

    def __init__(self, assignment):
        validator = AssignmentValidator()
        self._assignment = [validator.validate(var) for var in assignment]

    def assign(self, context, return_value):
        context.trace(lambda: 'Return: %s' % safe_repr(return_value))
        if self._assignment:
            resolver = ReturnValueResolver(self._assignment)
            self._assign(context, resolver.resolve(return_value))

    def _assign(self, context, return_value):
        for name, value in return_value:
            if not self._extended_assign(name, value, context.variables):
                value = self._normal_assign(name, value, context.variables)
            if name[0] == '&':
                continue   # TODO: .....
            context.info(format_assign_message(name, value))

    def _extended_assign(self, name, value, variables):
        if name[0] != '$' or '.' not in name or name in variables.store:
            return False
        base, attr = self._split_extended_assign(name)
        try:
            var = variables[base]
        except DataError:
            return False
        if not (self._variable_supports_extended_assign(var) and
                self._is_valid_extended_attribute(attr)):
            return False
        try:
            setattr(var, attr, value)
        except:
            raise DataError("Setting attribute '%s' to variable '%s' failed: %s"
                            % (attr, base, get_error_message()))
        return True

    def _split_extended_assign(self, name):
        base, attr = name.rsplit('.', 1)
        return base.strip() + '}', attr[:-1].strip()

    def _variable_supports_extended_assign(self, var):
        return not isinstance(var, (basestring, int, long, float))

    def _is_valid_extended_attribute(self, attr):
        return self._valid_extended_attr.match(attr) is not None

    def _normal_assign(self, name, value, variables):
        variables[name] = value
        return variables[name]


class AssignmentValidator(object):

    def __init__(self):
        self._seen_list = False
        self._seen_dict = False
        self._seen_any_var = False
        self._seen_assign_mark = False

    def validate(self, variable):
        variable = self._validate_assign_mark(variable)
        self._validate_state(variable[0])
        return variable

    def _validate_assign_mark(self, variable):
        if self._seen_assign_mark:
            raise DataError("Assign mark '=' can be used only with the last variable.")
        self._seen_assign_mark = variable.endswith('=')
        return variable.rstrip('= ')

    def _validate_state(self, identifier):
        if self._seen_dict:
            raise DataError('Dictionary variable cannot be assigned with other variables.')
        elif identifier == '@':
            if self._seen_list:
                raise DataError('Assignment can contain only one list variable.')
            self._seen_list = True
        elif identifier == '&':
            if self._seen_any_var:
                raise DataError('Dictionary variable cannot be assigned with other variables.')
            self._seen_dict = True
        self._seen_any_var = True


class ReturnValueResolver(object):

    def __init__(self, assignment):
        self._assignment = assignment
        identifiers = [a[0] for a in assignment]
        self._list_index = identifiers.index('@') if '@' in identifiers else -1

    def resolve(self, return_value):
        if len(self._assignment) == 1:
            return self._one_variable(self._assignment[0], return_value)
        return self._multiple_variables(self._assignment, return_value)

    def _one_variable(self, variable, ret):
        if ret is None:
            ret = {'$': None, '@': [], '&': {}}[variable[0]]
        return [(variable, ret)]

    def _multiple_variables(self, variables, ret):
        min_count = len(variables)
        if self._list_index != -1:
            min_count -= 1
        if ret is None:
            ret = [None] * min_count
        else:
            ret = self._convert_to_list(ret)
        if self._list_index == -1 and len(ret) != min_count:
            raise DataError('Expected %d return values, got %d.'
                            % (min_count, len(ret)))
        if len(ret) < min_count:
            raise DataError('Expected at least %d return values, got %d.'
                            % (min_count, len(ret)))
        if self._list_index == -1:
            return zip(variables, ret)
        before_vars = variables[:self._list_index]
        after_vars = variables[self._list_index+1:]
        before_items = zip(before_vars, ret)
        list_items = (variables[self._list_index],
                      ret[len(before_vars):len(ret)-len(after_vars)])
        after_items = zip(after_vars, ret[-len(after_vars):])
        return before_items + [list_items] + after_items

    def _convert_to_list(self, ret):
        if isinstance(ret, basestring):
            self._raise_expected_list(ret)
        try:
            return list(ret)
        except TypeError:
            self._raise_expected_list(ret)

    def _raise_expected_list(self, ret):
        typ = 'string' if isinstance(ret, basestring) else type(ret).__name__
        self._raise('Expected list-like object, got %s instead.' % typ)

    def _raise_too_few_arguments(self, ret):
        self._raise('Need more values than %d.' % len(ret))

    def _raise(self, error):
        raise DataError('Cannot assign return values: %s' % error)
