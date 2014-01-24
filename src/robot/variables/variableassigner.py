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

from .isvar import is_list_var, is_scalar_var


class VariableAssigner(object):
    _valid_extended_attr = re.compile('^[_a-zA-Z]\w*$')

    def __init__(self, assign):
        ap = AssignParser(assign)
        self.scalar_vars = ap.scalar_vars
        self.list_var = ap.list_var

    def assign(self, context, return_value):
        context.trace(lambda: 'Return: %s' % safe_repr(return_value))
        if self.scalar_vars or self.list_var:
            self._assign(context, ReturnValue(self.scalar_vars, self.list_var,
                                              return_value))

    def _assign(self, context, return_value):
        for name, value in return_value.get_variables_to_set():
            if not self._extended_assign(name, value, context.variables):
                self._normal_assign(name, value, context.variables)
            context.info(format_assign_message(name, value))

    def _extended_assign(self, name, value, variables):
        if '.' not in name or name.startswith('@') \
                or variables.contains(name, extended=False):
            return False
        base, attr = self._split_extended_assign(name)
        if not variables.contains(base, extended=True):
            return False
        var = variables[base]
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


class AssignParser(object):

    def __init__(self, assign):
        self.scalar_vars = []
        self.list_var = None
        self._assign_mark_used = False
        for var in assign:
            self._verify_items_allowed_only_on_last_round()
            var = self._strip_possible_assign_mark(var)
            self._set(var)

    def _verify_items_allowed_only_on_last_round(self):
        if self._assign_mark_used:
            raise DataError("Assign mark '=' can be used only with the last variable.")
        if self.list_var:
            raise DataError('Only the last variable to assign can be a list variable.')

    def _strip_possible_assign_mark(self, variable):
        if not variable.endswith('='):
            return variable
        self._assign_mark_used = True
        return variable.rstrip('= ')

    def _set(self, variable):
        if is_scalar_var(variable):
            self.scalar_vars.append(variable)
        elif is_list_var(variable):
            self.list_var = variable
        else:
            raise DataError('Invalid variable to assign: %s' % variable)


class ReturnValue(object):

    def __init__(self, scalar_vars, list_var, return_value):
        self._scalars = scalar_vars
        self._list = list_var
        self._return = return_value

    def get_variables_to_set(self):
        if self._return is None:
            return self._return_value_is_none(self._scalars, self._list)
        if len(self._scalars) == 1 and not self._list:
            return self._only_one_variable(self._scalars[0], self._return)
        ret = self._convert_to_list(self._return)
        if not self._list:
            return self._only_scalars(self._scalars, ret)
        if not self._scalars:
            return self._only_one_variable(self._list, ret)
        return self._scalars_and_list(self._scalars, self._list, ret)

    def _return_value_is_none(self, scalars, list_):
        ret = [(var, None) for var in scalars]
        if self._list:
            ret.append((list_, []))
        return ret

    def _only_one_variable(self, variable, ret):
        return [(variable, ret)]

    def _convert_to_list(self, ret):
        if isinstance(ret, basestring):
            self._raise_expected_list(ret)
        try:
            return list(ret)
        except TypeError:
            self._raise_expected_list(ret)

    def _only_scalars(self, scalars, ret):
        needed = len(scalars)
        if len(ret) < needed:
            self._raise_too_few_arguments(ret)
        if len(ret) == needed:
            return zip(scalars, ret)
        return zip(scalars[:-1], ret) + [(scalars[-1], ret[needed-1:])]

    def _scalars_and_list(self, scalars, list_, ret):
        if len(ret) < len(scalars):
            self._raise_too_few_arguments(ret)
        return zip(scalars, ret) + [(list_, ret[len(scalars):])]

    def _raise_expected_list(self, ret):
        typ = 'string' if isinstance(ret, basestring) else type(ret).__name__
        self._raise('Expected list-like object, got %s instead.' % typ)

    def _raise_too_few_arguments(self, ret):
        self._raise('Need more values than %d.' % len(ret))

    def _raise(self, error):
        raise DataError('Cannot assign return values: %s' % error)
