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


class NamedArgumentResolver(object):

    def __init__(self, argspec):
        self._argspec = argspec

    def resolve(self, values):
        named = {}
        positional = []
        for index, arg in enumerate(values):
            if self._is_named(arg):
                self._add_named(arg, named)
            elif named:
                self._raise_named_before_positional_error(index, values)
            else:
                positional.append(arg)
        return positional, named

    def _is_named(self, arg):
        if self._is_str_with_kwarg_sep(arg):
            name, _ = self._split_from_kwarg_sep(arg)
            return self._is_arg_name(name)
        return False

    def _add_named(self, arg, named):
        name, value = self._parse_named(arg)
        if name in named:
            raise DataError("Argument '%s' repeated for %s '%s'."
                            % (name, self._argspec.type.lower(), self._argspec.name))
        named[name] = value

    def _raise_named_before_positional_error(self, index, values):
        argument = values[index - 1]
        name, _ = self._split_from_kwarg_sep(argument)
        # TODO: Proof-read error message
        raise DataError("Error in %s '%s'. Named arguments can not be given "
                        "before positional arguments. Please remove prefix "
                        "%s= or escape %s as %s."
                        % (self._argspec.type.lower(), self._argspec.name, name,
                           argument, argument.replace('=', '\\=')))   # FIXME: replace only once

    def _optional(self, values):
        return values[self._argspec.minargs:]

    def _parse_named(self, arg):
        name, value = self._split_from_kwarg_sep(arg)
        return self._coerce(name), value

    def _coerce(self, name):
        return str(name)

    def _is_str_with_kwarg_sep(self, arg):
        if not isinstance(arg, basestring): #FIXME: Do we need this check?
            return False
        if '=' not in arg:
            return False
        if '=' not in arg.split('\\=', 1)[0]:
            return False
        return True

    def _split_from_kwarg_sep(self, arg):
        return arg.split('=', 1)

    def _is_arg_name(self, name):
        return self._arg_name(name) in self._argspec.positional or self._argspec.kwargs

    def _arg_name(self, name):
        return name


class UserKeywordNamedArgumentResolver(NamedArgumentResolver):

    def _arg_name(self, name):
        return '${%s}' % name

    def _coerce(self, name):
        return '${%s}' % name
