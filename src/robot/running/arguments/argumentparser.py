#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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
from robot.utils import PY2
from robot.variables import is_dict_var, is_list_var, is_scalar_var

from .argumentspec import ArgumentSpec


class _ArgumentParser(object):

    def __init__(self, type='Keyword'):
        self._type = type

    def parse(self, source, name=None):
        raise NotImplementedError


class PythonArgumentParser(_ArgumentParser):

    def parse(self, handler, name=None):
        if PY2:
            args, varargs, varkw, defaults = inspect.getargspec(handler)
            kwonlyargs = kwonlydefaults = annotations = None
        else:
            args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, \
                    annotations = inspect.getfullargspec(handler)
        if inspect.ismethod(handler) or handler.__name__ == '__init__':
            args = args[1:]  # drop 'self'
        defaults = list(defaults) if defaults else []
        return ArgumentSpec(name, self._type,
                            positional=args,
                            defaults=defaults,
                            varargs=varargs,
                            kwargs=varkw,
                            kwonlyargs=kwonlyargs,
                            kwonlydefaults=kwonlydefaults,
                            annotations=annotations)


class JavaArgumentParser(_ArgumentParser):

    def parse(self, signatures, name=None):
        if not signatures:
            return self._no_signatures_arg_spec(name)
        elif len(signatures) == 1:
            return self._single_signature_arg_spec(signatures[0], name)
        else:
            return self._multi_signature_arg_spec(signatures, name)

    def _no_signatures_arg_spec(self, name):
        # Happens when a class has no public constructors
        return self._format_arg_spec(name)

    def _single_signature_arg_spec(self, signature, name):
        varargs, kwargs = self._get_varargs_and_kwargs_support(signature.args)
        positional = len(signature.args) - int(varargs) - int(kwargs)
        return self._format_arg_spec(name, positional, varargs=varargs,
                                     kwargs=kwargs)

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

    def _multi_signature_arg_spec(self, signatures, name):
        mina = maxa = len(signatures[0].args)
        for sig in signatures[1:]:
            argc = len(sig.args)
            mina = min(argc, mina)
            maxa = max(argc, maxa)
        return self._format_arg_spec(name, maxa, maxa-mina)

    def _format_arg_spec(self, name, positional=0, defaults=0, varargs=False,
                         kwargs=False):
        positional = ['arg%d' % (i+1) for i in range(positional)]
        defaults = [''] * defaults
        return ArgumentSpec(name, self._type,
                            positional=positional,
                            defaults=defaults,
                            varargs='*varargs' if varargs else None,
                            kwargs='**kwargs' if kwargs else None,
                            supports_named=False)


class _ArgumentSpecParser(_ArgumentParser):

    def parse(self, argspec, name=None):
        result = ArgumentSpec(name, self._type)
        kw_only_args = False
        for arg in argspec:
            if result.kwargs:
                self._raise_invalid_spec('Only last argument can be kwargs.')
            elif self._is_kwargs(arg):
                self._add_kwargs(arg, result)
            elif self._is_kw_only_separator(arg):
                if result.varargs or kw_only_args:
                    self._raise_invalid_spec('Cannot have multiple varargs.')
                kw_only_args = True
            elif self._is_varargs(arg):
                if result.varargs or kw_only_args:
                    self._raise_invalid_spec('Cannot have multiple varargs.')
                self._add_varargs(arg, result)
                kw_only_args = True
            elif '=' in arg:
                self._add_arg_with_default(arg, result, kw_only_args)
            elif result.defaults and not kw_only_args:
                self._raise_invalid_spec('Non-default argument after default '
                                         'arguments.')
            else:
                self._add_arg(arg, result, kw_only_args)
        return result

    def _raise_invalid_spec(self, error):
        raise DataError('Invalid argument specification: %s' % error)

    def _is_kwargs(self, arg):
        raise NotImplementedError

    def _add_kwargs(self, kwargs, result):
        result.kwargs = self._format_kwargs(kwargs)

    def _format_kwargs(self, kwargs):
        raise NotImplementedError

    def _is_kw_only_separator(self, arg):
        raise NotImplementedError

    def _is_varargs(self, arg):
        raise NotImplementedError

    def _add_varargs(self, varargs, result):
        result.varargs = self._format_varargs(varargs)

    def _format_varargs(self, varargs):
        raise NotImplementedError

    def _add_arg_with_default(self, arg, result, kw_only_arg=False):
        arg, default = arg.split('=', 1)
        self._add_arg(arg, result, kw_only_arg)
        if not kw_only_arg:
            result.defaults.append(default)
        else:
            arg = self._format_arg(arg)
            result.kwonlydefaults[arg] = default

    def _format_arg(self, arg):
        return arg

    def _add_arg(self, arg, result, kw_only_arg=False):
        target = result.positional if not kw_only_arg else result.kwonlyargs
        target.append(self._format_arg(arg))


class DynamicArgumentParser(_ArgumentSpecParser):

    def _is_kwargs(self, arg):
        return arg.startswith('**')

    def _format_kwargs(self, kwargs):
        return kwargs[2:]

    def _is_kw_only_separator(self, arg):
        return arg == '*'

    def _is_varargs(self, arg):
        return arg.startswith('*') and not self._is_kwargs(arg)

    def _format_varargs(self, varargs):
        return varargs[1:]


class UserKeywordArgumentParser(_ArgumentSpecParser):

    def _is_kwargs(self, arg):
        return is_dict_var(arg)

    def _format_kwargs(self, kwargs):
        return kwargs[2:-1]

    def _is_varargs(self, arg):
        return is_list_var(arg)

    def _format_varargs(self, varargs):
        return varargs[2:-1]

    def _is_kw_only_separator(self, arg):
        return arg == '@{}'

    def _format_arg(self, arg):
        if not is_scalar_var(arg):
            self._raise_invalid_spec("Invalid argument syntax '%s'." % arg)
        return arg[2:-1]
