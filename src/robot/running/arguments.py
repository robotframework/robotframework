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

    def resolve(self, args, variables=None):
        posargs, namedargs = self._get_argument_resolver().resolve(args, variables)
        self.check_arg_limits(posargs, namedargs)
        return posargs, namedargs

    def check_arg_limits(self, args, namedargs={}):
        arg_count = len(args) + len(namedargs)
        if not self.minargs <= arg_count <= self.maxargs:
            self._raise_inv_args(arg_count)
        return args

    def _raise_inv_args(self, arg_count):
        minend = utils.plural_or_not(self.minargs)
        if self.minargs == self.maxargs:
            exptxt = "%d argument%s" % (self.minargs, minend)
        elif self.maxargs != sys.maxint:
            exptxt = "%d to %d arguments" % (self.minargs, self.maxargs)
        else:
            exptxt = "at least %d argument%s" % (self.minargs, minend)
        raise DataError("%s '%s' expected %s, got %d."
                        % (self._type, self._name, exptxt, arg_count))


class PythonKeywordArguments(_KeywordArguments):

    def _get_argument_resolver(self):
        return PythonKeywordArgumentResolver(self)

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
        self.arg_coercer = ArgumentCoercer(self._get_signatures(handler_method))

    def _get_argument_resolver(self):
        return JavaKeywordArgumentResolver(self)

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


class DynamicKeywordArguments(_KeywordArguments):

    def _get_argument_resolver(self):
        return PythonKeywordArgumentResolver(self)

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

    def set_to(self, variables, arguments):
        template_with_defaults = self._template_for(variables)
        template, positional, named = self._fill(template_with_defaults, arguments)
        self._check_missing_args(template, len(arguments))
        self.check_arg_limits(template)
        self._set_variables(variables, template)
        return self._resolve_variables(positional, named, variables)

    def _resolve_variables(self, positional, named, variables):
        posargs = variables.replace_list(positional)
        for name, value in named.items():
            named[name] = variables.replace_scalar(value)
        return posargs, named

    def _check_missing_args(self, template, arg_count):
        for a in template:
            if isinstance(a, _MissingArg):
                self._raise_inv_args(arg_count)

    def _template_for(self, variables):
        return [ _MissingArg() for _ in range(len(self.names)-len(self.defaults)) ] \
                + list(self.defaults)

    def _set_variables(self, variables, arg_values):
        if self._vararg:
            variables[self._vararg] = variables.replace_list(self._get_varargs(arg_values))
            arg_values = arg_values[:len(self.names)]
        for name, value in zip(self.names, arg_values):
            variables[name] = variables.replace_scalar(value)

    def _fill(self, template, arguments):
        varargs = arguments[len(template):]
        arg_resolver = UserKeywordArgumentResolver(self)
        positional, named = arg_resolver.resolve(arguments[:len(template)])
        for name, value in named.items():
            template[self.names.index(name)] = value
        for index, value in enumerate(positional):
            template[index] = value
        return template + varargs, positional, named

    def _get_varargs(self, args):
        return args[len(self.names):]


class PythonInitArguments(PythonKeywordArguments):
    _type = 'Test Library'


class JavaInitArguments(JavaKeywordArguments):
    _type = 'Test Library'

    def resolve(self, args):
        self.check_arg_limits(args)
        return args, {}


class _MissingArg(object):
    def __getattr__(self, name):
        raise RuntimeError()


class _ArgumentResolver(object):

    def __init__(self, arguments):
        self._arguments = arguments
        self._mand_arg_count = len(arguments.names) - len(arguments.defaults)

    def resolve(self, values, variables=None):
        positional, named = self._resolve_argument_usage(values)
        return self._resolve_variables(positional, named, variables)

    def _resolve_argument_usage(self, values):
        positional = []
        named = {}
        named_args_allowed = True
        for arg in reversed(self._optional(values)):
            if named_args_allowed and self._is_named(arg):
                name, value = self._parse_named(arg)
                if name in named:
                    raise RuntimeError('Keyword argument %s repeated.' % name)
                named[name] = value
            else:
                positional.append(self._parse_positional(arg))
                named_args_allowed = False
        positional = self._mandatory(values) + list(reversed(positional))
        return positional, named

    def _optional(self, values):
        return values[self._mand_arg_count:]

    def _mandatory(self, values):
        return values[:self._mand_arg_count]

    def _is_named(self, arg):
        if self._is_str_with_kwarg_sep(arg):
            name, _ = self._split_from_kwarg_sep(arg)
            return self._is_arg_name(name)
        return False

    def _parse_named(self, arg):
        name, value = self._split_from_kwarg_sep(arg)
        return self._coerce(name), value

    def _is_str_with_kwarg_sep(self, arg):
        if not isinstance(arg, basestring):
            return False
        if not '=' in arg:
            return False
        return True

    def _split_from_kwarg_sep(self, arg):
        return arg.split('=', 1)

    def _parse_positional(self, argstr):
        if self._is_str_with_kwarg_sep(argstr):
            name, _ = self._split_from_kwarg_sep(argstr)
            if self._is_arg_name(name[:-1]):
                return argstr.replace('\\=', '=')
        return argstr

    def _is_arg_name(self, name):
        return self._arg_name(name) in self._arguments.names

    def _resolve_variables(self, posargs, kwargs, variables):
        posargs = self._replace_list(posargs, variables)
        for name, value in kwargs.items():
            kwargs[name] = self._replace_scalar(value, variables)
        return posargs, kwargs

    def _replace_list(self, values, variables):
        return variables.replace_list(values) if variables else values

    def _replace_scalar(self, value, variables):
        return variables.replace_scalar(value) if variables else value


class UserKeywordArgumentResolver(_ArgumentResolver):

    def _arg_name(self, name):
        return '${%s}' % name

    def _coerce(self, name):
        return '${%s}' % name


class PythonKeywordArgumentResolver(_ArgumentResolver):

    def _arg_name(self, name):
        return name

    def _coerce(self, name):
        return str(name)


class JavaKeywordArgumentResolver(object):

    def __init__(self, arguments):
        self._arguments = arguments
        self._minargs, self._maxargs = arguments.minargs, arguments.maxargs

    def resolve(self, values, variables):
        values = variables.replace_list(values)
        self._arguments.check_arg_limits(values)
        return self._handle_varargs_and_coerce(values)

    def _handle_varargs_and_coerce(self, args):
        if self._maxargs == sys.maxint:
            args = self._handle_varargs(args)
        return self._arguments.arg_coercer(args), {}

    def _handle_varargs(self, args):
        if len(args) == self._minargs:
            args.append([])
        elif len(args) == self._minargs + 1 and utils.is_list(args[-1]):
            pass
        else:
            varargs = args[self._minargs:]
            args = args[:self._minargs]
            args.append(varargs)
        return args
