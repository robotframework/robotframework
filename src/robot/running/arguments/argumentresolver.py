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
from array import ArrayType

from .argumentvalidator import ArgumentValidator
from .namedargumentresolver import (NamedArgumentResolver,
                                    UserKeywordNamedArgumentResolver)


class ArgumentResolver(object):

    def __init__(self, argspec):
        self._named_resolver = NamedArgumentResolver(argspec)
        self._validator = ArgumentValidator(argspec)

    def resolve(self, arguments, variables):
        positional, named = self._named_resolver.resolve(arguments)
        positional, named = self._resolve_variables(variables, positional, named)
        self._validator.validate_arguments(positional, named)
        return positional, named

    def _resolve_variables(self, variables, positional, named):
        # TODO: Why/when can variables be None?
        if variables:
            positional = variables.replace_list(positional)
            named = dict((name, variables.replace_scalar(value))
                         for name, value in named.items())
        return positional, named


# TODO: Do we really need this class?
class UserKeywordArgumentResolver(ArgumentResolver):

    def __init__(self, argspec):
        ArgumentResolver.__init__(self, argspec)
        self._named_resolver = UserKeywordNamedArgumentResolver(argspec)


class RunKeywordArgumentResolver(object):

    def __init__(self, argspec, argument_resolution_index):
        self._validator = ArgumentValidator(argspec)
        self._resolution_index = argument_resolution_index

    def resolve(self, arguments, variables):
        arguments = self._resolve_variables(variables, arguments)
        self._validator.check_arg_limits(arguments)
        return arguments, {}

    def _resolve_variables(self, variables, arguments):
        return variables.replace_run_kw_info(arguments, self._resolution_index)


class JavaArgumentResolver(object):

    def __init__(self, argspec):
        self._validator = ArgumentValidator(argspec)
        self._argspec = argspec

    def resolve(self, arguments, variables):
        arguments = self._resolve_variables(variables, arguments)
        self._validator.check_arg_limits(arguments)
        self._handle_varargs(arguments)
        return arguments, {}

    def _resolve_variables(self, variables, arguments):
        # TODO: Why/when can variables be None
        if variables:
            arguments = variables.replace_list(arguments)
        return arguments

    # TODO: Could coercer handle this?
    def _handle_varargs(self, arguments):
        if self._expects_varargs() and self._last_is_not_list(arguments):
            minargs = self._argspec.minargs
            arguments[minargs:] = [arguments[minargs:]]
        return arguments, {}

    def _expects_varargs(self):
        return self._argspec.maxargs == sys.maxint

    def _last_is_not_list(self, args):
        return not (len(args) == self._argspec.minargs + 1
                    and isinstance(args[-1], (list, tuple, ArrayType)))
