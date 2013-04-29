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

    def resolve(self, arguments):
        positional = []
        named = {}
        for arg in arguments:
            if self._is_named(arg):
                self._add_named(arg, named)
            elif named:
                self._raise_positional_after_named()
            else:
                positional.append(arg)
        return positional, named

    def _is_named(self, arg):
        # TODO: When is arg not string??
        if not isinstance(arg, basestring) or '=' not in arg:
            return False
        name = arg.split('=')[0]
        if self._is_escaped(name):
            return False
        return (self._arg_name(name) in self._argspec.positional
                or self._argspec.kwargs)

    def _is_escaped(self, name):
        return name.endswith('\\')

    def _arg_name(self, name):
        try:
            return str(name)
        except UnicodeError:
            return name    # FIXME: Better non-ASCII handling needed

    def _add_named(self, arg, named):
        name, value = self._split_named(arg)
        if name in named:
            self._raise_multiple_values(name)
        named[name] = value

    def _split_named(self, arg):
        name, value = arg.split('=', 1)
        return self._arg_name(name), value

    def _raise_multiple_values(self, name):
        raise DataError("%s '%s' got multiple values for argument '%s'."
                        % (self._argspec.type, self._argspec.name, name))

    def _raise_positional_after_named(self):
        raise DataError("%s '%s' got positional argument after named arguments."
                        % (self._argspec.type, self._argspec.name))


class UserKeywordNamedArgumentResolver(NamedArgumentResolver):

    def _arg_name(self, name):
        return '${%s}' % name
