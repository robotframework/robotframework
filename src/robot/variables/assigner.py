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

import re

from robot.errors import (DataError, ExecutionStatus, HandlerExecutionFailed,
                          VariableError)
from robot.utils import (ErrorDetails, format_assign_message, get_error_message,
                         is_number, is_string, prepr, rstrip, type_name)


class VariableAssignment(object):

    def __init__(self, assignment):
        validator = AssignmentValidator()
        try:
            self.assignment = [validator.validate(var) for var in assignment]
            self.error = None
        except DataError as err:
            self.assignment = assignment
            self.error = err

    def __iter__(self):
        return iter(self.assignment)

    def __len__(self):
        return len(self.assignment)

    def validate_assignment(self):
        if self.error:
            raise self.error

    def assigner(self, context):
        self.validate_assignment()
        return VariableAssigner(self.assignment, context)


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
        if variable.endswith('='):
            self._seen_assign_mark = True
            return rstrip(variable[:-1])
        return variable

    def _validate_state(self, is_list, is_dict):
        if is_list and self._seen_list:
            raise DataError('Assignment can contain only one list variable.')
        if self._seen_dict or is_dict and self._seen_any_var:
            raise DataError('Dictionary variable cannot be assigned with '
                            'other variables.')
        self._seen_list += is_list
        self._seen_dict += is_dict
        self._seen_any_var = True


class VariableAssigner(object):
    _valid_extended_attr = re.compile(r'^[_a-zA-Z]\w*$')

    def __init__(self, assignment, context):
        self._assignment = assignment
        self._context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            return
        failure = self._get_failure(exc_type, exc_val, exc_tb)
        if failure.can_continue(self._context):
            self.assign(failure.return_value)

    def _get_failure(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, ExecutionStatus):
            return exc_val
        exc_info = (exc_type, exc_val, exc_tb)
        return HandlerExecutionFailed(ErrorDetails(exc_info))

    def assign(self, return_value):
        context = self._context
        context.trace(lambda: 'Return: %s' % prepr(return_value))
        resolver = ReturnValueResolver(self._assignment)
        for name, value in resolver.resolve(return_value):
            if not self._extended_assign(name, value, context.variables):
                value = self._normal_assign(name, value, context.variables)
            context.info(format_assign_message(name, value))

    def _extended_assign(self, name, value, variables):
        if name[0] != '$' or '.' not in name or name in variables:
            return False
        base, attr = [token.strip() for token in name[2:-1].rsplit('.', 1)]
        try:
            var = variables.replace_scalar('${%s}' % base)
        except VariableError:
            return False
        if not (self._variable_supports_extended_assign(var) and
                self._is_valid_extended_attribute(attr)):
            return False
        try:
            setattr(var, attr, value)
        except:
            raise VariableError("Setting attribute '%s' to variable '${%s}' failed: %s"
                                % (attr, base, get_error_message()))
        return True

    def _variable_supports_extended_assign(self, var):
        return not (is_string(var) or is_number(var))

    def _is_valid_extended_attribute(self, attr):
        return self._valid_extended_attr.match(attr) is not None

    def _normal_assign(self, name, value, variables):
        variables[name] = value
        # Always return the actually assigned value.
        return value if name[0] == '$' else variables[name]


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
        if is_string(return_value):
            self._raise_expected_list(return_value)
        try:
            return list(return_value)
        except TypeError:
            self._raise_expected_list(return_value)

    def _raise_expected_list(self, ret):
        self._raise('Expected list-like value, got %s.' % type_name(ret))

    def _raise(self, error):
        raise VariableError('Cannot set variables: %s' % error)

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
        return list(zip(self._variables, return_value))


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
        before = list(zip(before_vars, before_items))
        after = list(zip(after_vars, after_items))
        return before + [(list_var, list_items)] + after

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
