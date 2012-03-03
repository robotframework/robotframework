#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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
from robot.variables import is_list_var, is_scalar_var
from robot.utils import safe_repr, format_assign_message, get_error_message


class VariableAssigner(object):

    def __init__(self, assign):
        ap = AssignParser(assign)
        self.scalar_vars = ap.scalar_vars
        self.list_var = ap.list_var

    def assign(self, context, return_value):
        context.trace('Return: %s' % safe_repr(return_value))
        if self.scalar_vars or self.list_var:
            self._assign(context, return_value)

    def _assign(self, context, return_value):
        variables = context.get_current_vars()
        for name, value in self._get_vars_to_set(return_value):
            if not self._extended_assign(name, value, variables):
                self._normal_assign(name, value, variables)
            context.output.info(format_assign_message(name, value))

    def _get_vars_to_set(self, ret):
        if ret is None:
            return self._get_vars_to_set_when_ret_is_none()
        if not self.list_var:
            return self._get_vars_to_set_with_only_scalars(ret)
        if self._is_non_string_iterable(ret):
            return self._get_vars_to_set_with_scalars_and_list(list(ret))
        self._raise_invalid_return_value(ret, wrong_type=True)

    def _is_non_string_iterable(self, value):
        if isinstance(value, basestring):
            return False
        try:
            iter(value)
        except TypeError:
            return False
        else:
            return True

    def _get_vars_to_set_when_ret_is_none(self):
        ret = [(var, None) for var in self.scalar_vars]
        if self.list_var:
            ret.append((self.list_var, []))
        return ret

    def _get_vars_to_set_with_only_scalars(self, ret):
        needed = len(self.scalar_vars)
        if needed == 1:
            return [(self.scalar_vars[0], ret)]
        if not self._is_non_string_iterable(ret):
            self._raise_invalid_return_value(ret, wrong_type=True)
        ret = list(ret)
        if len(ret) < needed:
            self._raise_invalid_return_value(ret)
        if len(ret) == needed:
            return zip(self.scalar_vars, ret)
        return zip(self.scalar_vars[:-1], ret) \
                    + [(self.scalar_vars[-1], ret[needed-1:])]

    def _get_vars_to_set_with_scalars_and_list(self, ret):
        needed_scalars = len(self.scalar_vars)
        if not needed_scalars:
            return [(self.list_var, ret)]
        if len(ret) < needed_scalars:
            self._raise_invalid_return_value(ret)
        return zip(self.scalar_vars, ret) \
                    + [(self.list_var, ret[needed_scalars:])]

    def _raise_invalid_return_value(self, ret, wrong_type=False):
        if wrong_type:
            err = 'Expected list-like object, got %s instead' % type(ret).__name__
        else:
            err = 'Need more values than %d' % len(ret)
        raise DataError("Cannot assign return values: %s." % err)

    def _extended_assign(self, name, value, variables):
        if '.' not in name or variables.contains(name, extended=False):
            return False
        base, attr = self._split_extended_assign(name)
        if not variables.contains(base, extended=True):
            return False
        var = variables[base]
        if isinstance(var, (basestring, int, long, float)):
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
