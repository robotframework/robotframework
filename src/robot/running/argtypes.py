#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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

class _ArgTypeResolver(object):

    def __init__(self, arguments, values):
        self._names = arguments.names
        mand_arg_count = len(arguments.names) - len(arguments.defaults)
        self._optional_values = values[mand_arg_count:]
        posargs, self.kwargs = self._resolve_optional_args()
        self.posargs = values[:mand_arg_count] + list(posargs)

    def _resolve_optional_args(self):
        posargs = []
        kwargs = {}
        kwargs_allowed = True
        for arg in reversed(self._optional_values):
            if kwargs_allowed and self._is_kwarg(arg):
                name, value = self._parse_kwarg(arg)
                if name in kwargs:
                    raise RuntimeError('Keyword argument %s repeated.' % name)
                kwargs[name] = value
            else:
                posargs.append(self._parse_posarg(arg))
                kwargs_allowed = False
        return reversed(posargs), kwargs

    def _is_kwarg(self, arg):
        if self._is_str_with_kwarg_sep(arg):
            name, _ = self._split_from_kwarg_sep(arg)
            return self._is_arg_name(name)
        return False

    def _is_str_with_kwarg_sep(self, arg):
        if not isinstance(arg, basestring):
            return False
        if not '=' in arg:
            return False
        return True

    def _split_from_kwarg_sep(self, arg):
        return arg.split('=', 1)

    def _parse_posarg(self, argstr):
        if self._is_str_with_kwarg_sep(argstr):
            name, _ = self._split_from_kwarg_sep(argstr)
            if self._is_arg_name(name[:-1]):
                return argstr.replace('\\=', '=')
        return argstr

    def _is_arg_name(self, name):
        return self._arg_name(name) in self._names

    def _parse_kwarg(self, arg):
        name, value = self._split_from_kwarg_sep(arg)
        return self._coerce(name), value

class UserKeywordArgTypeResolver(_ArgTypeResolver):

    def _arg_name(self, name):
        return '${%s}' % name

    def _coerce(self, name):
        return '${%s}' % name

class LibraryKeywordArgTypeResolver(_ArgTypeResolver):

    def _arg_name(self, name):
        return name

    def _coerce(self, name):
        return str(name)
