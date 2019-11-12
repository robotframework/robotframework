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

from robot.errors import DataError
from robot.utils import JYTHON, PY_VERSION, PY2
from robot.variables import is_dict_var, is_list_var, is_scalar_var

from .argumentspec import ArgumentSpec


if PY2:
    from inspect import getargspec, ismethod

    def getfullargspec(func):
        return getargspec(func) + ([], None, {})
else:
    from inspect import getfullargspec, ismethod

if PY_VERSION >= (3, 5):
    import typing
else:
    typing = None

if JYTHON:
    from java.lang import Class
    from java.util import List, Map


class _ArgumentParser(object):

    def __init__(self, type='Keyword'):
        self._type = type

    def parse(self, source, name=None):
        raise NotImplementedError


class PythonArgumentParser(_ArgumentParser):

    def parse(self, handler, name=None):
        args, varargs, kwargs, defaults, kwonly, kwonlydefaults, annotations \
                = getfullargspec(handler)
        if ismethod(handler) or handler.__name__ == '__init__':
            args = args[1:]  # drop 'self'
        spec = ArgumentSpec(
            name,
            self._type,
            positional=args,
            varargs=varargs,
            kwargs=kwargs,
            kwonlyargs=kwonly,
            defaults=self._get_defaults(args, defaults, kwonlydefaults)
        )
        spec.types = self._get_types(handler, annotations, spec)
        return spec

    def _get_defaults(self, args, default_values, kwonlydefaults):
        if default_values:
            defaults = dict(zip(args[-len(default_values):], default_values))
        else:
            defaults = {}
        if kwonlydefaults:
            defaults.update(kwonlydefaults)
        return defaults

    def _get_types(self, handler, annotations, spec):
        types = getattr(handler, 'robot_types', ())
        if types is None:
            return None
        if types:
            return types
        return self._get_type_hints(handler, annotations, spec)

    def _get_type_hints(self, handler, annotations, spec):
        if not typing:
            return annotations
        try:
            type_hints = typing.get_type_hints(handler)
        except Exception:  # Can raise pretty much anything
            return annotations
        self._remove_mismatching_type_hints(type_hints, spec.argument_names)
        self._remove_optional_none_type_hints(type_hints, spec.defaults)
        return type_hints

    def _remove_mismatching_type_hints(self, type_hints, argument_names):
        # typing.get_type_hints returns info from the original function even
        # if it is decorated. Argument names are got from the wrapping
        # decorator and thus there is a mismatch that needs to be resolved.
        mismatch = set(type_hints) - set(argument_names)
        for name in mismatch:
            type_hints.pop(name)

    def _remove_optional_none_type_hints(self, type_hints, defaults):
        # If argument has None as a default, typing.get_type_hints adds
        # optional None to the information it returns. We don't want that.
        for arg in defaults:
            if defaults[arg] is None and arg in type_hints:
                type_ = type_hints[arg]
                if self._is_union(type_):
                    types = type_.__args__
                    if len(types) == 2 and types[1] is type(None):
                        type_hints[arg] = types[0]

    def _is_union(self, type_):
        if PY_VERSION >= (3, 7) and hasattr(type_, '__origin__'):
            type_ = type_.__origin__
        return isinstance(type_, type(typing.Union))


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
        if defaults:
            defaults = {name: '' for name in positional[-defaults:]}
        else:
            defaults = {}
        return ArgumentSpec(name, self._type,
                            positional=positional,
                            varargs='varargs' if varargs else None,
                            kwargs='kwargs' if kwargs else None,
                            defaults=defaults,
                            supports_named=False)


class _ArgumentSpecParser(_ArgumentParser):

    def parse(self, argspec, name=None):
        spec = ArgumentSpec(name, self._type)
        kw_only_args = False
        for arg in argspec:
            if spec.kwargs:
                self._raise_invalid_spec('Only last argument can be kwargs.')
            elif self._is_kwargs(arg):
                self._add_kwargs(spec, arg)
            elif self._is_kw_only_separator(arg):
                if spec.varargs or kw_only_args:
                    self._raise_invalid_spec('Cannot have multiple varargs.')
                kw_only_args = True
            elif self._is_varargs(arg):
                if spec.varargs or kw_only_args:
                    self._raise_invalid_spec('Cannot have multiple varargs.')
                self._add_varargs(spec, arg)
                kw_only_args = True
            elif '=' in arg:
                self._add_arg_with_default(spec, arg, kw_only_args)
            elif spec.defaults and not kw_only_args:
                self._raise_invalid_spec('Non-default argument after default '
                                         'arguments.')
            else:
                self._add_arg(spec, arg, kw_only_args)
        return spec

    def _raise_invalid_spec(self, error):
        raise DataError('Invalid argument specification: %s' % error)

    def _is_kwargs(self, arg):
        raise NotImplementedError

    def _add_kwargs(self, spec, kwargs):
        spec.kwargs = self._format_kwargs(kwargs)

    def _format_kwargs(self, kwargs):
        raise NotImplementedError

    def _is_kw_only_separator(self, arg):
        raise NotImplementedError

    def _is_varargs(self, arg):
        raise NotImplementedError

    def _add_varargs(self, spec, varargs):
        spec.varargs = self._format_varargs(varargs)

    def _format_varargs(self, varargs):
        raise NotImplementedError

    def _add_arg_with_default(self, spec, arg, kw_only_arg=False):
        arg, default = arg.split('=', 1)
        arg = self._add_arg(spec, arg, kw_only_arg)
        spec.defaults[arg] = default

    def _format_arg(self, arg):
        return arg

    def _add_arg(self, spec, arg, kw_only_arg=False):
        arg = self._format_arg(arg)
        target = spec.positional if not kw_only_arg else spec.kwonlyargs
        target.append(arg)
        return arg


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
