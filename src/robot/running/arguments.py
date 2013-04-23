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

import sys
import inspect
from array import ArrayType

from robot.errors import DataError, FrameworkError
from robot.variables import is_list_var, is_scalar_var
from robot import utils


class KeywordArguments(object):

    def __init__(self, name, type='Keyword', positional=None, defaults=None,
                 varargs=None, kwargs=None, minargs=None, maxargs=None):
        self.name = name
        self.type = type
        self.positional = positional or []
        self.names = self.positional   # FIXME: Remove
        self.defaults = defaults or []
        self.varargs = varargs
        self.kwargs = kwargs
        self._minargs = minargs
        self._maxargs = maxargs

    @property
    def minargs(self):
        if self._minargs is None:
            self._minargs = len(self.positional) - len(self.defaults)
        return self._minargs

    @property
    def maxargs(self):
        if self._maxargs is None:
            self._maxargs = len(self.positional) \
                if not (self.varargs or self.kwargs) else sys.maxint
        return self._maxargs

    # FIXME: Move logging elsewhere
    def trace_log_args(self, logger, positional, named):
        message = lambda: self._get_trace_log_arg_message(positional, named)
        logger.trace(message)

    def _get_trace_log_arg_message(self, positional, named):
        args = [utils.safe_repr(arg) for arg in positional]
        if named:
            args += ['%s=%s' % (utils.unic(name), utils.safe_repr(value))
                     for name, value in named.items()]
        return 'Arguments: [ %s ]' % ' | '.join(args)

    def trace_log_uk_args(self, logger, variables):
        message = lambda: self._get_trace_log_uk_arg_message(variables)
        logger.trace(message)

    def _get_trace_log_uk_arg_message(self, variables):
        names = self.names + ([self.varargs] if self.varargs else [])
        args = ['%s=%s' % (name, utils.safe_repr(variables[name]))
                for name in names]
        return 'Arguments: [ %s ]' % ' | '.join(args)


class _ArgumentParser(object):

    def __init__(self, type='Keyword'):
        self._type = type

    def parse(self, name, source):
        raise NotImplementedError


class PythonArgumentParser(_ArgumentParser):

    def parse(self, name, source):
        return KeywordArguments(name, self._type, *self._get_arg_spec(source))

    def _get_arg_spec(self, handler):
        """Returns info about args in a tuple (args, defaults, varargs, kwargs)

        args     - list of all accepted arguments except varargs
        defaults - list of default values
        varargs  - name of the argument accepting varargs or None
        kwargs   - name of the argument accepting kwargs or None
        """
        args, varargs, kwargs, defaults = inspect.getargspec(handler)
        if inspect.ismethod(handler):
            args = args[1:]  # drop 'self'
        defaults = list(defaults) if defaults else []
        return args, defaults, varargs, kwargs


class JavaArgumentParser(_ArgumentParser):

    def parse(self, name, signatures):
        minargs, maxargs = self._get_arg_limits(signatures)
        return KeywordArguments(name, self._type, minargs=minargs, maxargs=maxargs)

    def _get_arg_limits(self, signatures):
        if not signatures:
            return self._no_signatures_arg_limits()
        elif len(signatures) == 1:
            return self._get_single_signature_arg_limits(signatures[0])
        else:
            return self._get_multi_signature_arg_limits(signatures)

    def _no_signatures_arg_limits(self):
        # Happens when a class has no public constructors
        return 0, 0

    def _get_single_signature_arg_limits(self, signature):
        args = signature.args
        if args and args[-1].isArray():
            mina = len(args) - 1
            maxa = sys.maxint
        else:
            mina = maxa = len(args)
        return mina, maxa

    def _get_multi_signature_arg_limits(self, signatures):
        mina = maxa = len(signatures[0].args)
        for sig in signatures[1:]:
            argc = len(sig.args)
            mina = min(argc, mina)
            maxa = max(argc, maxa)
        return mina, maxa


class _ArgumentSpecParser(_ArgumentParser):

    def parse(self, name, argspec):
        result = KeywordArguments(name, self._type)
        for arg in argspec:
            if result.varargs:
                raise DataError('Only last argument can be varargs.')
            if self._is_varargs(arg):
                self._add_varargs(arg, result)
                continue
            if '=' in arg:
                self._add_arg_with_default(arg, result)
                continue
            if result.defaults:
                raise DataError('Non-default argument after default arguments.')
            self._add_arg(arg, result)
        return result

    def _is_varargs(self, arg):
        raise NotImplementedError

    def _add_varargs(self, varargs, result):
        result.varargs = self._format_varargs(varargs)

    def _format_varargs(self, varargs):
        return varargs

    def _add_arg_with_default(self, arg, result):
        arg, default = arg.split('=', 1)
        self._add_arg(arg, result)
        result.defaults.append(default)

    def _add_arg(self, arg, result):
        if not self._is_valid_arg(arg):
            raise DataError("Invalid argument '%s'." % arg)
        result.positional.append(arg)

    def _is_valid_arg(self, arg):
        return True


class DynamicArgumentParser(_ArgumentSpecParser):

    def _is_varargs(self, arg):
        return arg.startswith('*')

    def _format_varargs(self, varargs):
        return varargs[1:]


class UserKeywordArgumentParser(_ArgumentSpecParser):

    def _is_varargs(self, arg):
        return is_list_var(arg)

    def _is_valid_arg(self, arg):
        return is_scalar_var(arg)


class Foo:   # FIXME: We perhaps need to rename this class.........

    def __init__(self, argspec):
        self._argspec = argspec

    def resolve(self, arguments, variables):
        positional, named = self._resolve_arg_usage(arguments, variables)
        positional, varargs = self._split_args_and_varargs(positional)
        argument_values = self._resolve_arg_values(variables, named, positional)
        argument_values += varargs
        ArgumentLimitChecker(self._argspec).check_missing_args(argument_values, len(arguments))
        return argument_values

    def _resolve_arg_usage(self, arguments, variables):
        resolver = UserKeywordArgumentResolver(self._argspec)
        return resolver.resolve(arguments, variables)

    def _split_args_and_varargs(self, args):
        if not self._argspec.varargs:
            return args, []
        index = len(self._argspec.positional)
        return args[:index], args[index:]

    def _resolve_arg_values(self, variables, named, positional):
        template = self._template_for(variables)
        for name, value in named.items():
            template.set_value(self._argspec.positional.index(name), value)
        for index, value in enumerate(positional):
            template.set_value(index, value)
        return template.as_list()

    def _template_for(self, variables):
        defaults = variables.replace_list(list(self._argspec.defaults))
        return UserKeywordArgsTemplate(self._argspec.minargs, defaults)


class _MissingArg(object):
    def __getattr__(self, name):
        raise DataError


class UserKeywordArgsTemplate(object):

    def __init__(self, minargs, defaults):
        self._template = [_MissingArg() for _ in range(minargs)] + defaults
        self._already_set = set()

    def set_value(self, idx, value):
        if idx in self._already_set:
            raise FrameworkError
        self._already_set.add(idx)
        self._template[idx] = value

    def as_list(self):
        return self._template


class _ArgumentResolver(object):

    def __init__(self, arguments):
        self._arguments = arguments
        self._mand_arg_count = arguments.minargs  # TODO: Remove or property
        self._arg_limit_checker = ArgumentLimitChecker(arguments)

    @property
    def _name(self):
        return self._arguments.name

    @property
    def _type(self):
        return self._arguments.type

    def resolve(self, values, variables=None):
        positional, named = self._resolve_argument_usage(values)
        positional, named = self._resolve_variables(positional, named, variables)
        self._arg_limit_checker.check_arg_limits(positional, named)
        return positional, named

    def _resolve_argument_usage(self, values):
        named, positional = self._populate_positional_and_named(values)
        self._check_mandatories(positional, named)
        return positional, named

    def _populate_positional_and_named(self, values):
        named = {}
        positional = []
        used_positionally = set()
        for index, arg in enumerate(values):
            if self._is_named(arg):
                self._add_named(arg, named, used_positionally)
            elif named:
                self._raise_named_before_positional_error(index, values)
            else:
                self._add_positional(arg, index, positional, used_positionally)
        return named, positional

    def _is_named(self, arg):
        if self._is_str_with_kwarg_sep(arg):
            name, _ = self._split_from_kwarg_sep(arg)
            return self._is_arg_name(name)
        return False

    def _add_named(self, arg, named, used_positionally):
        name, value = self._parse_named(arg)
        if name in named:
            raise DataError("Argument '%s' repeated for %s '%s'."
                            % (name, self._type.lower(), self._name))
        if name in used_positionally:
            raise DataError("Error in %s '%s'. Value for argument '%s' was given twice."
                            % (self._type.lower(), self._name, name))
        named[name] = value

    def _add_positional(self, arg, index, positional, used_positionally):
        if index < len(self._arguments.names):
            positional_name = self._arguments.names[index]
            used_positionally.add(positional_name)
        positional.append(arg)

    def _raise_named_before_positional_error(self, index, values):
        argument = values[index - 1]
        name, _ = self._split_from_kwarg_sep(argument)
        raise DataError("Error in %s '%s'. Named arguments can not be given "
                        "before positional arguments. Please remove prefix "
                        "%s= or escape %s as %s."
                        % (self._type.lower(), self._name, name,
                           argument, argument.replace('=', '\\=')))   # FIXME: replace only once

    def _check_mandatories(self, positional, named):
        if len(positional) >= self._mand_arg_count:
            return
        # TODO: Would it be better to check args after resolving vars?
        # Wouldn't need to care about list vars in that case.
        if any(is_list_var(arg) for arg in positional):
            return
        for name in self._arguments.names[len(positional):self._mand_arg_count]:
            if name not in named:
                raise DataError("%s '%s' missing value for argument '%s'."
                                % (self._type, self._name, name))

    def _optional(self, values):
        return values[self._mand_arg_count:]

    def _parse_named(self, arg):
        name, value = self._split_from_kwarg_sep(arg)
        return self._coerce(name), value

    def _is_str_with_kwarg_sep(self, arg):
        if not isinstance(arg, basestring): #FIXME: Do we need this check?
            return False
        if '=' not in arg:
            return False
        if '=' not in arg.split('\\=',1)[0]:
            return False
        return True

    def _split_from_kwarg_sep(self, arg):
        return arg.split('=', 1)

    def _is_arg_name(self, name):
        return self._arg_name(name) in self._arguments.positional or self._kwargs_is_used()

    def _kwargs_is_used(self):
        return bool(self._arguments.kwargs)

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


class PythonArgumentResolver(_ArgumentResolver):

    def _arg_name(self, name):
        return name

    def _coerce(self, name):
        return str(name)


class DynamicArgumentResolver(PythonArgumentResolver):
    pass


class RunKeywordArgumentResolver(object):

    def __init__(self, arguments, arg_resolution_index):
        self._arg_limit_checker = ArgumentLimitChecker(arguments)
        self._arg_resolution_index = arg_resolution_index

    def resolve(self, values, variables):
        args = variables.replace_run_kw_info(values, self._arg_resolution_index)
        self._arg_limit_checker.check_arg_limits(args)
        return args, {}


class JavaArgumentResolver(object):

    def __init__(self, arguments):
        self._arguments = arguments
        self._minargs = arguments.minargs
        self._maxargs = arguments.maxargs

    def resolve(self, values, variables):
        if variables:  # FIXME: Why is variables None with test lib inits??
            values = variables.replace_list(values)
        ArgumentLimitChecker(self._arguments).check_arg_limits(values)
        if self._expects_varargs() and self._last_is_not_list(values):
            values[self._minargs:] = [values[self._minargs:]]
        return values, {}

    def _expects_varargs(self):
        return self._maxargs == sys.maxint

    def _last_is_not_list(self, args):
        return not (len(args) == self._minargs + 1
                    and isinstance(args[-1], (list, tuple, ArrayType)))


class ArgumentLimitChecker(object):

    def __init__(self, argspec):
        self._minargs = argspec.minargs
        self._maxargs = argspec.maxargs
        self._name = argspec.name
        self._type = argspec.type

    def check_arg_limits(self, args, namedargs=None):
        self._check_arg_limits(len(args) + len(namedargs or {}))

    def check_arg_limits_for_dry_run(self, args):
        arg_count = len(args)
        scalar_arg_count = len([a for a in args if not is_list_var(a)])
        if scalar_arg_count <= self._minargs and arg_count - scalar_arg_count:
            arg_count = self._minargs
        self._check_arg_limits(arg_count)

    def _check_arg_limits(self, arg_count):
        if not self._minargs <= arg_count <= self._maxargs:
            self._raise_inv_args(arg_count)

    def check_missing_args(self, args, arg_count):
        for a in args:
            if isinstance(a, _MissingArg):
                self._raise_inv_args(arg_count)

    def _raise_inv_args(self, arg_count):
        minend = utils.plural_or_not(self._minargs)
        if self._minargs == self._maxargs:
            exptxt = "%d argument%s" % (self._minargs, minend)
        elif self._maxargs != sys.maxint:
            exptxt = "%d to %d arguments" % (self._minargs, self._maxargs)
        else:
            exptxt = "at least %d argument%s" % (self._minargs, minend)
        raise DataError("%s '%s' expected %s, got %d."
                        % (self._type, self._name, exptxt, arg_count))
