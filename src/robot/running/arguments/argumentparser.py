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
from robot.utils import JYTHON, PY2, is_string, split_from_equals
from robot.variables import is_assign, is_scalar_assign

from .argumentspec import ArgumentSpec

# Move PythonArgumentParser to this module when Python 2 support is dropped.
if PY2:
    from .py2argumentparser import PythonArgumentParser
else:
    from .py3argumentparser import PythonArgumentParser

if JYTHON:
    from java.lang import Class
    from java.util import List, Map


class _ArgumentParser(object):

    def __init__(self, type='Keyword'):
        self._type = type

    def parse(self, source, name=None):
        raise NotImplementedError


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
                            positional_only=positional,
                            var_positional='varargs' if varargs else None,
                            var_named='kwargs' if kwargs else None,
                            defaults=defaults)


class _ArgumentSpecParser(_ArgumentParser):

    def __init__(self, type='Keyword', error_reporter=None):
        _ArgumentParser.__init__(self, type)
        self._error_reporter = error_reporter

    def parse(self, argspec, name=None):
        spec = ArgumentSpec(name, self._type)
        named_only = False
        for arg in argspec:
            arg = self._validate_arg(arg)
            if spec.var_named:
                self._report_error('Only last argument can be kwargs.')
            elif isinstance(arg, tuple):
                arg, default = arg
                arg = self._add_arg(spec, arg, named_only)
                spec.defaults[arg] = default
            elif self._is_kwargs(arg):
                spec.var_named = self._format_kwargs(arg)
            elif self._is_varargs(arg):
                if named_only:
                    self._report_error('Cannot have multiple varargs.')
                if not self._is_kw_only_separator(arg):
                    spec.var_positional = self._format_varargs(arg)
                named_only = True
            elif spec.defaults and not named_only:
                self._report_error('Non-default argument after default arguments.')
            else:
                self._add_arg(spec, arg, named_only)
        return spec

    def _validate_arg(self, arg):
        raise NotImplementedError

    def _report_error(self, error):
        if self._error_reporter:
            self._error_reporter(error)
        else:
            raise DataError('Invalid argument specification: %s' % error)

    def _is_kwargs(self, arg):
        raise NotImplementedError

    def _format_kwargs(self, kwargs):
        raise NotImplementedError

    def _is_kw_only_separator(self, arg):
        raise NotImplementedError

    def _is_varargs(self, arg):
        raise NotImplementedError

    def _format_varargs(self, varargs):
        raise NotImplementedError

    def _format_arg(self, arg):
        return arg

    def _add_arg(self, spec, arg, named_only=False):
        arg = self._format_arg(arg)
        target = spec.positional_or_named if not named_only else spec.named_only
        target.append(arg)
        return arg


class DynamicArgumentParser(_ArgumentSpecParser):

    def _validate_arg(self, arg):
        if isinstance(arg, tuple):
            if self._is_invalid_tuple(arg):
                self._report_error('Invalid argument "%s".' % (arg,))
            if len(arg) == 1:
                return arg[0]
            return arg
        if '=' in arg:
            return tuple(arg.split('=', 1))
        return arg

    def _is_invalid_tuple(self, arg):
        return (len(arg) > 2
                or not is_string(arg[0])
                or (arg[0].startswith('*') and len(arg) > 1))

    def _is_kwargs(self, arg):
        return arg.startswith('**')

    def _format_kwargs(self, kwargs):
        return kwargs[2:]

    def _is_varargs(self, arg):
        return arg.startswith('*')

    def _is_kw_only_separator(self, arg):
        return arg == '*'

    def _format_varargs(self, varargs):
        return varargs[1:]


class UserKeywordArgumentParser(_ArgumentSpecParser):

    def _validate_arg(self, arg):
        arg, default = split_from_equals(arg)
        if not (is_assign(arg) or arg == '@{}'):
            self._report_error("Invalid argument syntax '%s'." % arg)
        if default is None:
            return arg
        if not is_scalar_assign(arg):
            typ = 'list' if arg[0] == '@' else 'dictionary'
            self._report_error("Only normal arguments accept default values, "
                               "%s arguments like '%s' do not." % (typ, arg))
        return arg, default

    def _is_kwargs(self, arg):
        return arg[0] == '&'

    def _format_kwargs(self, kwargs):
        return kwargs[2:-1]

    def _is_varargs(self, arg):
        return arg[0] == '@'

    def _is_kw_only_separator(self, arg):
        return arg == '@{}'

    def _format_varargs(self, varargs):
        return varargs[2:-1]

    def _format_arg(self, arg):
        return arg[2:-1]
