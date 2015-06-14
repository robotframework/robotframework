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

import re

from robot.errors import DataError
from robot.utils import (format_assign_message, get_error_message, prepr,
                         type_name)


class VariableAssigner(object):
    _valid_extended_attr = re.compile('^[_a-zA-Z]\w*$')

    def __init__(self, assignment):
        validator = AssignmentValidator()
        try:
            self.assignment = [validator.validate(var) for var in assignment]
            self.error = None
        except DataError as err:
            self.assignment = assignment
            self.error = err

    def validate_assignment(self):
        if self.error:
            raise self.error

    def assign(self, context, return_value):
        self.validate_assignment()
        context.trace(lambda: 'Return: %s' % prepr(return_value))
        resolver = ReturnValueResolver(self.assignment)
        for name, value in resolver.resolve(return_value):
            if not self._extended_assign(name, value, context.variables):
                value = self._normal_assign(name, value, context.variables)
            context.info(format_assign_message(name, value))

    def _extended_assign(self, name, value, variables):
        if name[0] != '$' or '.' not in name or name in variables:
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
        self._validate_state(is_list=variable[0] == '@',
                             is_dict=variable[0] == '&')
        return variable

    def _validate_assign_mark(self, variable):
        if self._seen_assign_mark:
            raise DataError("Assign mark '=' can be used only with the last "
                            "variable.")
        self._seen_assign_mark = variable.endswith('=')
        return variable.rstrip('= ')

    def _validate_state(self, is_list, is_dict):
        if is_list and self._seen_list:
            raise DataError('Assignment can contain only one list variable.')
        if self._seen_dict or is_dict and self._seen_any_var:
            raise DataError('Dictionary variable cannot be assigned with '
                            'other variables.')
        self._seen_list += is_list
        self._seen_dict += is_dict
        self._seen_any_var = True


def ReturnValueResolver(assignment):
    if not assignment:
        return NoReturnValueResolver()
    if len(assignment) == 1:
        return OneReturnValueResolver(assignment[0])
    if any(a[0] == '@' for a in assignment):
        return ScalarsAndListReturnValueResolver(assignment)
    return ScalarsOnlyReturnValueResolver(assignment)


class NoReturnValueResolver(object):

    def resolve(self, return_value):
        return []


class OneReturnValueResolver(object):

    def __init__(self, variable):
        self._variable = variable

    def resolve(self, return_value):
        if return_value is None:
            identifier = self._variable[0]
            return_value = {'$': None, '@': [], '&': {}}[identifier]
        return [(self._variable, return_value)]


class _MultiReturnValueResolver(object):

    def __init__(self, variables):
        self._variables = variables
        self._min_count = len(variables)

    def resolve(self, return_value):
        return_value = self._convert_to_list(return_value)
        self._validate(len(return_value))
        return self._resolve(return_value)

    def _convert_to_list(self, return_value):
        if return_value is None:
            return [None] * self._min_count
        if isinstance(return_value, basestring):
            self._raise_expected_list(return_value)
        try:
            return list(return_value)
        except TypeError:
            self._raise_expected_list(return_value)

    def _raise_expected_list(self, ret):
        self._raise('Expected list-like value, got %s.' % type_name(ret))

    def _raise(self, error):
        raise DataError('Cannot set variables: %s' % error)

    def _validate(self, return_count):
        raise NotImplementedError

    def _resolve(self, return_value):
        raise NotImplementedError


class ScalarsOnlyReturnValueResolver(_MultiReturnValueResolver):

    def _validate(self, return_count):
        if return_count != self._min_count:
            self._raise('Expected %d return values, got %d.'
                        % (self._min_count, return_count))

    def _resolve(self, return_value):
        return zip(self._variables, return_value)


class ScalarsAndListReturnValueResolver(_MultiReturnValueResolver):

    def __init__(self, variables):
        _MultiReturnValueResolver.__init__(self, variables)
        self._min_count -= 1

    def _validate(self, return_count):
        if return_count < self._min_count:
            self._raise('Expected %d or more return values, got %d.'
                        % (self._min_count, return_count))

    def _resolve(self, return_value):
        before_vars, list_var, after_vars \
            = self._split_variables(self._variables)
        before_items, list_items, after_items \
            = self._split_return(return_value, before_vars, after_vars)
        return (zip(before_vars, before_items) +
                [(list_var, list_items)] +
                zip(after_vars, after_items))

    def _split_variables(self, variables):
        list_index = [v[0] for v in variables].index('@')
        return (variables[:list_index],
                variables[list_index],
                variables[list_index+1:])

    def _split_return(self, return_value, before_vars, after_vars):
        list_start = len(before_vars)
        list_end = len(return_value) - len(after_vars)
        return (return_value[:list_start],
                return_value[list_start:list_end],
                return_value[list_end:])
