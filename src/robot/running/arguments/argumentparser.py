#  Copyright 2008-2015 Nokia Solutions and Networks
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
if sys.platform.startswith('java'):
    from java.lang import Class
    from java.util import List, Map

from robot.errors import DataError
from robot.variables import is_dict_var, is_list_var, is_scalar_var

from .argumentspec import ArgumentSpec


class _ArgumentParser(object):

    def __init__(self, type='Keyword'):
        self._type = type

    def parse(self, source, name=None):
        return ArgumentSpec(name, self._type, *self._get_arg_spec(source))

    def _get_arg_spec(self, source):
        raise NotImplementedError


class PythonArgumentParser(_ArgumentParser):

    def _get_arg_spec(self, handler):
        args, varargs, kwargs, defaults = inspect.getargspec(handler)
        if inspect.ismethod(handler) or handler.__name__ == '__init__':
            args = args[1:]  # drop 'self'
        defaults = list(defaults) if defaults else []
        return args, defaults, varargs, kwargs


class JavaArgumentParser(_ArgumentParser):

    def _get_arg_spec(self, signatures):
        if not signatures:
            return self._no_signatures_arg_spec()
        elif len(signatures) == 1:
            return self._single_signature_arg_spec(signatures[0])
        else:
            return self._multi_signature_arg_spec(signatures)

    def _no_signatures_arg_spec(self):
        # Happens when a class has no public constructors
        return self._format_arg_spec()

    def _single_signature_arg_spec(self, signature):
        varargs, kwargs = self._get_varargs_and_kwargs_support(signature.args)
        positional = len(signature.args) - int(varargs) - int(kwargs)
        return self._format_arg_spec(positional, varargs=varargs, kwargs=kwargs)

    def _get_varargs_and_kwargs_support(self, args):
        if not args:
            return False, False
        if self._is_varargs_type(args[-1]):
            return True, False
        if not self._is_kwargs_type(args[-1]):
            return False, False
        if len(args) > 1 and self._is_varargs_type(args[-2]):
            return True, True
        return False, True

    def _is_varargs_type(self, arg):
        return arg is List or isinstance(arg, Class) and arg.isArray()

    def _is_kwargs_type(self, arg):
        return arg is Map

    def _multi_signature_arg_spec(self, signatures):
        mina = maxa = len(signatures[0].args)
        for sig in signatures[1:]:
            argc = len(sig.args)
            mina = min(argc, mina)
            maxa = max(argc, maxa)
        return self._format_arg_spec(maxa, maxa-mina)

    def _format_arg_spec(self, positional=0, defaults=0, varargs=False, kwargs=False):
        positional = ['arg%d' % (i+1) for i in range(positional)]
        defaults = [''] * defaults
        varargs = '*varargs' if varargs else None
        kwargs = '**kwargs' if kwargs else None
        supports_named = False
        return positional, defaults, varargs, kwargs, supports_named


class _ArgumentSpecParser(_ArgumentParser):

    def parse(self, argspec, name=None):
        result = ArgumentSpec(name, self._type)
        for arg in argspec:
            if result.kwargs:
                self._raise_invalid_spec('Only last argument can be kwargs.')
            if self._is_kwargs(arg):
                self._add_kwargs(arg, result)
                continue
            if result.varargs:
                self._raise_invalid_spec('Positional argument after varargs.')
            if self._is_varargs(arg):
                self._add_varargs(arg, result)
                continue
            if '=' in arg:
                self._add_arg_with_default(arg, result)
                continue
            if result.defaults:
                self._raise_invalid_spec('Non-default argument after default '
                                         'arguments.')
            self._add_arg(arg, result)
        return result

    def _raise_invalid_spec(self, error):
        raise DataError('Invalid argument specification: %s' % error)

    def _is_kwargs(self, arg):
        raise NotImplementedError

    def _add_kwargs(self, kwargs, result):
        result.kwargs = self._format_kwargs(kwargs)

    def _format_kwargs(self, kwargs):
        raise NotImplementedError

    def _is_varargs(self, arg):
        raise NotImplementedError

    def _add_varargs(self, varargs, result):
        result.varargs = self._format_varargs(varargs)

    def _format_varargs(self, varargs):
        raise NotImplementedError

    def _add_arg_with_default(self, arg, result):
        arg, default = arg.split('=', 1)
        self._add_arg(arg, result)
        result.defaults.append(default)

    def _add_arg(self, arg, result):
        result.positional.append(self._format_arg(arg))

    def _format_arg(self, arg):
        return arg


class DynamicArgumentParser(_ArgumentSpecParser):

    def _is_kwargs(self, arg):
        return arg.startswith('**')

    def _format_kwargs(self, kwargs):
        return kwargs[2:]

    def _is_varargs(self, arg):
        return arg.startswith('*') and not self._is_kwargs(arg)

    def _format_varargs(self, varargs):
        return varargs[1:]


class UserKeywordArgumentParser(_ArgumentSpecParser):

    def _is_kwargs(self, arg):
        return is_dict_var(arg)

    def _is_varargs(self, arg):
        return is_list_var(arg)

    def _format_kwargs(self, kwargs):
        return kwargs[2:-1]

    def _format_varargs(self, varargs):
        return varargs[2:-1]

    def _format_arg(self, arg):
        if not is_scalar_var(arg):
            self._raise_invalid_spec("Invalid argument syntax '%s'." % arg)
        return arg[2:-1]
