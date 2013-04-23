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


class PythonArgumentResolver(object):

    def __init__(self, argspec):
        self._named_resolver = NamedArgumentResolver(argspec)
        self._validator = ArgumentValidator(argspec)

    def resolve(self, arguments, variables):
        positional, named = self._named_resolver.resolve(arguments)
        positional, named = self._resolve_variables(positional, named, variables)
        self._validator.validate_arguments(positional, named)
        return positional, named

    def _resolve_variables(self, posargs, kwargs, variables):
        posargs = self._replace_list(posargs, variables)
        for name, value in kwargs.items():
            kwargs[name] = self._replace_scalar(value, variables)
        return posargs, kwargs

    def _replace_list(self, values, variables):
        # TODO: Why can variables be None??
        return variables.replace_list(values) if variables else values

    def _replace_scalar(self, value, variables):
        return variables.replace_scalar(value) if variables else value


class DynamicArgumentResolver(PythonArgumentResolver):
    pass


class UserKeywordArgumentResolver(PythonArgumentResolver):

    def __init__(self, argspec):
        self._named_resolver = UserKeywordNamedArgumentResolver(argspec)
        self._validator = ArgumentValidator(argspec)
        self._mapper = ArgumentMapper(argspec)

    def resolve(self, arguments, variables):
        positional, named = PythonArgumentResolver.resolve(self, arguments, variables)
        return self._mapper.map_arguments(positional, named, variables)


class RunKeywordArgumentResolver(object):

    def __init__(self, arguments, arg_resolution_index):
        self._arg_limit_checker = ArgumentValidator(arguments)
        self._arg_resolution_index = arg_resolution_index

    def resolve(self, values, variables):
        args = variables.replace_run_kw_info(values, self._arg_resolution_index)
        self._arg_limit_checker.check_arg_limits(args)
        return args, {}


class JavaArgumentResolver(object):

    def __init__(self, argspec):
        self._argspec = argspec

    def resolve(self, arguments, variables):
        if variables:  # FIXME: Why is variables None with test lib inits??
            arguments = variables.replace_list(arguments)
        ArgumentValidator(self._argspec).check_arg_limits(arguments)
        self._handle_varargs(arguments)
        return arguments, {}

    def _handle_varargs(self, arguments):
        if self._expects_varargs() and self._last_is_not_list(arguments):
            minargs = self._argspec.minargs
            arguments[minargs:] = [arguments[minargs:]]
        return arguments, {}

    def _expects_varargs(self):
        return self._argspec.maxargs == sys.maxint

    def _last_is_not_list(self, args, minargs):
        return not (len(args) == self._argspec.minargs + 1
                    and isinstance(args[-1], (list, tuple, ArrayType)))


class ArgumentMapper(object):

    def __init__(self, argspec):
        self._argspec = argspec

    def map_arguments(self, positional, named, variables):
        template = KeywordCallTemplate(self._argspec, variables)
        template.fill_positional(positional)
        template.fill_named(named)
        return list(template)


class KeywordCallTemplate(object):

    def __init__(self, argspec, variables):
        defaults = variables.replace_list(argspec.defaults)
        self._template = [None] * argspec.minargs + defaults
        self._positional = argspec.positional

    def fill_positional(self, positional):
        self._template[:len(positional)] = positional

    def fill_named(self, named):
        for name, value in named.items():
            index = self._positional.index(name)
            self._template[index] = value

    def __iter__(self):
        return iter(self._template)


class ArgumentValidator(object):

    def __init__(self, argspec):
        self._argspec = argspec
        self._minargs = argspec.minargs
        self._maxargs = argspec.maxargs
        self._name = argspec.name
        self._type = argspec.type

    def validate_arguments(self, positional, named):
        self._check_mandatories(positional, named)
        self.check_arg_limits(positional, named)

    def _check_mandatories(self, positional, named):
        minargs = self._argspec.minargs
        for name in self._argspec.positional[len(positional):minargs]:
            if name not in named:
                raise DataError("%s '%s' missing value for argument '%s'."
                                % (self._argspec.type, self._argspec.name, name))
        for name in self._argspec.positional[:len(positional)]:
            if name in named:
                raise DataError("Error in %s '%s'. Value for argument '%s' was given twice."
                                % (self._argspec.type.lower(), self._argspec.name, name))

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
