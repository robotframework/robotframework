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

import sys
from types import MethodType, FunctionType

from robot.errors import DataError, FrameworkError
from robot import utils

if utils.is_jython:
    from javaargcoercer import ArgumentCoercer


class _KeywordArguments(object):
    _type = 'Keyword'

    def __init__(self, argument_source, kw_or_lib_name):
        self.names, self.defaults, self.varargs, self.minargs, self.maxargs \
            = self._determine_args(argument_source)
        self._name = kw_or_lib_name

    def _determine_args(self, argument_source):
        return [], [], None, 0, 0

    def resolve(self, args, variables=None):
        self.check_arg_limits(args)
        return args, {}

    def check_arg_limits(self, args):
        if not self.minargs <= len(args) <= self.maxargs:
            self._raise_inv_args(args)
        return args

    def _raise_inv_args(self, args):
        minend = utils.plural_or_not(self.minargs)
        if self.minargs == self.maxargs:
            exptxt = "%d argument%s" % (self.minargs, minend)
        elif self.maxargs != sys.maxint:
            exptxt = "%d to %d arguments" % (self.minargs, self.maxargs)
        else:
            exptxt = "at least %d argument%s" % (self.minargs, minend)
        raise DataError("%s '%s' expected %s, got %d."
                        % (self._type, self._name, exptxt, len(args)))


class PythonKeywordArguments(_KeywordArguments):

    def resolve(self, args, variables):
        args = variables.replace_list(args)
        self.check_arg_limits(args)
        arg_resolver = LibraryKeywordArgTypeResolver(self, args)
        return arg_resolver.posargs, arg_resolver.kwargs

    def _determine_args(self, handler_method):
        args, defaults, varargs = self._get_arg_spec(handler_method)
        minargs = len(args) - len(defaults)
        maxargs = varargs is not None and sys.maxint or len(args)
        return args, defaults, varargs, minargs, maxargs

    def _get_arg_spec(self, handler):
        """Returns info about args in a tuple (args, defaults, varargs)

        args     - tuple of all accepted arguments
        defaults - tuple of default values
        varargs  - name of the argument accepting varargs or None
        """
        # Code below is based on inspect module's getargs and getargspec
        # methods. See their documentation and/or source for more details.
        if type(handler) is MethodType:
            func = handler.im_func
            first_arg = 1        # this drops 'self' from methods' args
        elif type(handler) is FunctionType:
            func = handler
            first_arg = 0
        else:
            raise FrameworkError("Only MethodType and FunctionType accepted. "
                                 "Got '%s' instead." % type(handler))
        co = func.func_code
        nargs = co.co_argcount
        args = co.co_varnames[first_arg:nargs]
        defaults = func.func_defaults
        if defaults is None:
            defaults = ()
        if co.co_flags & 4:                      # 4 == CO_VARARGS
            varargs =  co.co_varnames[nargs]
        else:
            varargs = None
        return args, defaults, varargs


class JavaKeywordArguments(_KeywordArguments):

    def __init__(self, handler_method, name):
        _KeywordArguments.__init__(self, handler_method, name)
        self._arg_coercer = ArgumentCoercer(self._get_signatures(handler_method))

    def resolve(self, args, variables):
        args = self._replace_vars_from_args(args, variables)
        self.check_arg_limits(args)
        arg_resolver = LibraryKeywordArgTypeResolver(self, args)
        return arg_resolver.posargs, arg_resolver.kwargs

    def _replace_vars_from_args(self, args, variables):
        args = variables.replace_list(args)
        self.check_arg_limits(args)
        if self.maxargs == sys.maxint:
            args = self._handle_varargs(args)
        return self.coerce(args)

    def _handle_varargs(self, args):
        if len(args) == self.minargs:
            args.append([])
        elif len(args) == self.minargs + 1 and utils.is_list(args[-1]):
            pass
        else:
            varargs = args[self.minargs:]
            args = args[:self.minargs]
            args.append(varargs)
        return args

    def _determine_args(self, handler_method):
        signatures = self._get_signatures(handler_method)
        minargs, maxargs = self._get_arg_limits(signatures)
        return [], [], None, minargs, maxargs

    def _get_signatures(self, handler):
        co = self._get_code_object(handler)
        return co.argslist[:co.nargs]

    def _get_code_object(self, handler):
        try:
            return handler.im_func
        except AttributeError:
            return handler

    def _get_arg_limits(self, signatures):
        if len(signatures) == 1:
            return self._get_single_sig_arg_limits(signatures[0])
        else:
            return self._get_multi_sig_arg_limits(signatures)

    def _get_single_sig_arg_limits(self, signature):
        args = signature.args
        if len(args) > 0 and args[-1].isArray():
            mina = len(args) - 1
            maxa = sys.maxint
        else:
            mina = maxa = len(args)
        return mina, maxa

    def _get_multi_sig_arg_limits(self, signatures):
        mina = maxa = None
        for sig in signatures:
            argc = len(sig.args)
            if mina is None or argc < mina:
                mina = argc
            if maxa is None or argc > maxa:
                maxa = argc
        return mina, maxa

    def coerce(self, args):
        return self._arg_coercer(args)


class DynamicKeywordArguments(_KeywordArguments):

    def _determine_args(self, argspec):
        args, defaults, varargs = self._get_arg_spec(argspec)
        minargs = len(args) - len(defaults)
        maxargs = varargs is not None and sys.maxint or len(args)
        return args, defaults, varargs, minargs, maxargs

    def _get_arg_spec(self, argspec):
        if argspec is None:
            return [], [], '<unknown>'
        try:
            if utils.is_str(argspec):
                raise TypeError
            return self._parse_arg_spec(list(argspec))
        except TypeError:
            raise TypeError('Argument specification should be list/array of Strings.')

    def _parse_arg_spec(self, argspec):
        if argspec == []:
            return [], [], None
        args = []
        defaults = []
        vararg = None
        for token in argspec:
            if vararg is not None:
                raise TypeError
            if token.startswith('*'):
                vararg = token[1:]
                continue
            if token.count('=') > 0:
                arg, default = token.split('=', 1)
                args.append(arg)
                defaults.append(default)
                continue
            if defaults:
                raise TypeError
            args.append(token)
        return args, defaults, vararg


class UserKeywordArguments(_KeywordArguments):

    def __init__(self, argnames, defaults, vararg, minargs, maxargs, name):
        self.names = list(argnames) # Python 2.5 does not support indexing tuples
        self.defaults = defaults
        self._vararg = vararg
        self.minargs = minargs
        self.maxargs = maxargs
        self._name = name

    def set_to(self, variables, argument_values):
        template_with_defaults = self._template_for(variables)
        argument_values = self._set_possible_varargs(template_with_defaults,
                                                     variables, argument_values)
        self._set_variables(variables, self._fill(template_with_defaults,
                                                  argument_values))

    def _template_for(self, variables):
        return [ _MissingArg() for _ in range(len(self.names)-len(self.defaults)) ] +\
                 list(variables.replace_list(self.defaults))

    def _set_possible_varargs(self, template, variables, argument_values):
        if self._vararg:
            variables[self._vararg] = self._get_varargs(argument_values)
            argument_values = argument_values[:len(template)]
        return argument_values

    def _set_variables(self, variables, args):
        for name, value in zip(self.names, args):
            variables[name] = value

    def _fill(self, template, arguments):
        arg_resolver = UserKeywordArgTypeResolver(self, arguments)
        for name, value in arg_resolver.kwargs.items():
            template[self.names.index(name)] = value
        for index, value in enumerate(arg_resolver.posargs):
            template[index] = value
        return template

    def _get_varargs(self, args):
        return args[len(self.names):]


class PythonInitArguments(PythonKeywordArguments):
    _type = 'Test Library'

    def resolve(self, args):
        self.check_arg_limits(args)
        arg_resolver = LibraryKeywordArgTypeResolver(self, args)
        return arg_resolver.posargs, arg_resolver.kwargs


class JavaInitArguments(JavaKeywordArguments):
    _type = 'Test Library'

    def resolve(self, args):
        self.check_arg_limits(args)
        arg_resolver = LibraryKeywordArgTypeResolver(self, args)
        return arg_resolver.posargs, arg_resolver.kwargs


class _MissingArg(object):
    def __getattr__(self, name):
        raise RuntimeError()


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
