#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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
import inspect
from array import ArrayType

from robot.errors import DataError
from robot.variables import is_list_var, is_scalar_var
from robot import utils

if utils.is_jython:
    from javaargcoercer import ArgumentCoercer


class _KeywordArguments(object):
    _type = 'Keyword'

    def __init__(self, argument_source, kw_or_lib_name):
        self.names, self.defaults, self.varargs, self.minargs, self.maxargs \
            = self._determine_args(argument_source)
        self._arg_limit_checker = _ArgLimitChecker(self.minargs, self.maxargs,
                                                   kw_or_lib_name, self._type)

    def resolve(self, args, variables, output=None):
        posargs, namedargs = self._resolve(args, variables)
        self.check_arg_limits(posargs, namedargs)
        self._tracelog_args(output, posargs, namedargs)
        return posargs, namedargs

    def _resolve(self, args, variables):
        return self._get_argument_resolver().resolve(args, variables)

    def check_arg_limits(self, args, namedargs={}):
        self._arg_limit_checker.check_arg_limits(args, namedargs)

    def check_arg_limits_for_dry_run(self, args):
        self._arg_limit_checker.check_arg_limits_for_dry_run(args)

    def _tracelog_args(self, logger, posargs, namedargs={}):
        if self._logger_not_available_during_library_init(logger):
            return
        args = [ utils.safe_repr(a) for a in posargs ] \
             + [ '%s=%s' % (utils.unic(a), utils.safe_repr(namedargs[a]))
                 for a in namedargs ]
        logger.trace('Arguments: [ %s ]' % ' | '.join(args))

    def _logger_not_available_during_library_init(self, logger):
        return not logger


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

        args     - list of all accepted arguments except varargs
        defaults - list of default values
        varargs  - name of the argument accepting varargs or None
        """
        args, varargs, _, defaults = inspect.getargspec(handler)
        if inspect.ismethod(handler):
            args = args[1:]  # drop 'self'
        defaults = list(defaults) if defaults else []
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
            if isinstance(argspec, basestring):
                raise TypeError
            return self._parse_arg_spec(list(argspec))
        except TypeError:
            raise TypeError('Argument spec should be a list/array of strings')

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
            if '=' in token:
                arg, default = token.split('=', 1)
                args.append(arg)
                defaults.append(default)
                continue
            if defaults:
                raise TypeError
            args.append(token)
        return args, defaults, vararg


class RunKeywordArguments(PythonKeywordArguments):

    def __init__(self, argument_source, name, arg_resolution_index):
        PythonKeywordArguments.__init__(self, argument_source, name)
        self._arg_resolution_index = arg_resolution_index

    def _resolve(self, args, variables):
        args = variables.replace_from_beginning(self._arg_resolution_index, args)
        return args, {}


class PythonInitArguments(PythonKeywordArguments):
    _type = 'Test Library'


class JavaInitArguments(JavaKeywordArguments):
    _type = 'Test Library'

    def resolve(self, args, variables=None):
        if variables:
            args = variables.replace_list(args)
        self.check_arg_limits(args)
        return args, {}


class UserKeywordArguments(object):

    def __init__(self, args, name):
        self.names, self.defaults, self.varargs = self._get_arg_spec(args)
        self.minargs = len(self.names) - len(self.defaults)
        maxargs = self.varargs is not None and sys.maxint or len(self.names)
        self._arg_limit_checker = _ArgLimitChecker(self.minargs, maxargs,
                                                   name, 'Keyword')

    def _get_arg_spec(self, origargs):
        """Returns argument spec in a tuple (args, defaults, varargs).

        args     - tuple of all accepted arguments
        defaults - tuple of default values
        varargs  - name of the argument accepting varargs or None

        Examples:
          ['${arg1}', '${arg2}']
            => ('${arg1}', '${arg2}'), (), None
          ['${arg1}', '${arg2}=default', '@{varargs}']
            => ('${arg1}', '${arg2}'), ('default',), '@{varargs}'
        """
        args = []
        defaults = []
        varargs = None
        for arg in origargs:
            if varargs:
                raise DataError('Only last argument can be a list')
            if is_list_var(arg):
                varargs = arg
                continue   # should be last round (otherwise DataError in next)
            arg, default = self._split_default(arg)
            if defaults and default is None:
                raise DataError('Non default argument after default arguments')
            if not is_scalar_var(arg):
                raise DataError("Invalid argument '%s'" % arg)
            args.append(arg)
            if default is not None:
                defaults.append(default)
        return args, defaults, varargs

    def _split_default(self, arg):
        if '=' not in arg:
            return arg, None
        return arg.split('=', 1)

    def resolve_arguments_for_dry_run(self, arguments):
        self._arg_limit_checker.check_arg_limits_for_dry_run(arguments)
        required_number_of_args = self.minargs + len(self.defaults)
        needed_args = required_number_of_args - len(arguments)
        if needed_args > 0:
            return self._fill_missing_args(arguments, needed_args)
        return arguments

    def _fill_missing_args(self, arguments, needed):
        return arguments + needed * [None]

    def resolve(self, arguments, variables):
        positional, varargs, named = self._resolve_arg_usage(arguments, variables)
        self._arg_limit_checker.check_arg_limits(positional+varargs, named)
        argument_values = self._resolve_arg_values(variables, named, positional)
        argument_values += varargs
        self._arg_limit_checker.check_missing_args(argument_values, len(arguments))
        return argument_values

    def _template_for(self, variables):
        return [ _MissingArg() for _ in range(self.minargs) ] \
                + variables.replace_list(list(self.defaults))

    def _resolve_arg_values(self, variables, named, positional):
        template = self._template_for(variables)
        for name, value in named.items():
            template[self.names.index(name)] = value
        for index, value in enumerate(positional):
            template[index] = value
        return template

    def _resolve_arg_usage(self, arguments, variables):
        resolver = UserKeywordArgumentResolver(self)
        positional, named = self._replace_variables(variables,
                                                    *resolver.resolve(arguments))
        return self._split_args_and_varargs(positional) + (named,)

    def _replace_variables(self, variables, positional, named):
        for name in named:
            named[name] = variables.replace_scalar(named[name])
        return variables.replace_list(positional), named

    def set_variables(self, arg_values, variables, output):
        before_varargs, varargs = self._split_args_and_varargs(arg_values)
        for name, value in zip(self.names, before_varargs):
            variables[name] = value
        if self.varargs:
            variables[self.varargs] = varargs
        self._tracelog_args(output, variables)

    def _split_args_and_varargs(self, args):
        if not self.varargs:
            return args, []
        return args[:len(self.names)], args[len(self.names):]

    def _tracelog_args(self, logger, variables):
        arguments_string = self._get_arguments_as_string(variables)
        logger.trace('Arguments: [ %s ]' % arguments_string)

    def _get_arguments_as_string(self, variables):
        args = []
        for name in self.names + ([self.varargs] if self.varargs else []):
            args.append('%s=%s' % (name, utils.safe_repr(variables[name])))
        return ' | '.join(args)


class _MissingArg(object):
    def __getattr__(self, name):
        raise RuntimeError


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
                positional.append(arg)
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
        if '=' not in arg:
            return False
        return True

    def _split_from_kwarg_sep(self, arg):
        return arg.split('=', 1)

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
        if self._expects_varargs() and self._last_is_not_list(values):
            values[self._minargs:] = [values[self._minargs:]]
        return self._arguments.arg_coercer(values), {}

    def _expects_varargs(self):
        return self._maxargs == sys.maxint

    def _last_is_not_list(self, args):
        return not (len(args) == self._minargs + 1
                    and isinstance(args[-1], (list, tuple, ArrayType)))


class _ArgLimitChecker(object):

    def __init__(self, minargs, maxargs, name, type_):
        self.minargs = minargs
        self.maxargs = maxargs
        self._name = name
        self._type = type_

    def check_arg_limits(self, args, namedargs={}):
        self._check_arg_limits(len(args) + len(namedargs))

    def check_arg_limits_for_dry_run(self, args):
        arg_count = len(args)
        scalar_arg_count = len([a for a in args if not is_list_var(a)])
        if scalar_arg_count <= self.minargs and arg_count - scalar_arg_count:
            arg_count = self.minargs
        self._check_arg_limits(arg_count)

    def _check_arg_limits(self, arg_count):
        if not self.minargs <= arg_count <= self.maxargs:
            self._raise_inv_args(arg_count)

    def check_missing_args(self, args, arg_count):
        for a in args:
            if isinstance(a, _MissingArg):
                self._raise_inv_args(arg_count)

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
