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

import inspect

from robot.errors import DataError
from robot.variables import is_list_var, is_scalar_var

from .argumentspec import ArgumentSpec


class _ArgumentParser(object):

    def __init__(self, type='Keyword'):
        self._type = type

    def parse(self, name, source):
        return ArgumentSpec(name, self._type, *self._get_arg_spec(source))

    def _get_arg_spec(self, source):
        raise NotImplementedError


class PythonArgumentParser(_ArgumentParser):

    def _get_arg_spec(self, handler):
        args, varargs, kwargs, defaults = inspect.getargspec(handler)
        if inspect.ismethod(handler):
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
        args = signature.args
        if args and args[-1].isArray():
            return self._format_arg_spec(len(args)-1, varargs=True)
        return self._format_arg_spec(len(args))

    def _multi_signature_arg_spec(self, signatures):
        mina = maxa = len(signatures[0].args)
        for sig in signatures[1:]:
            argc = len(sig.args)
            mina = min(argc, mina)
            maxa = max(argc, maxa)
        return self._format_arg_spec(maxa, maxa-mina)

    def _format_arg_spec(self, positional=0, defaults=0, varargs=False):
        positional = ['arg%d' % (i+1) for i in range(positional)]
        defaults = [''] * defaults
        varargs = '*varargs' if varargs else None
        return positional, defaults, varargs


class _ArgumentSpecParser(_ArgumentParser):

    def parse(self, name, argspec):
        result = ArgumentSpec(name, self._type)
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
