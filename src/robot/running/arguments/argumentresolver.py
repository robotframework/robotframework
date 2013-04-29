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

from .argumentvalidator import ArgumentValidator
from .namedargumentresolver import NamedArgumentResolver


class ArgumentResolver(object):

    def __init__(self, argspec, resolve_variables_until=None):
        self._named_resolver = NamedArgumentResolver(argspec)
        self._validator = ArgumentValidator(argspec)
        self._resolve_variables_until = resolve_variables_until

    def resolve(self, arguments, variables):
        positional, named = self._named_resolver.resolve(arguments)
        positional, named = self._resolve_variables(variables, positional, named)
        self._validator.validate_arguments(positional, named)
        return positional, named

    def _resolve_variables(self, variables, positional, named):
        # TODO: Why/when can variables be None?
        if variables:
            positional = variables.replace_list(positional,
                                                self._resolve_variables_until)
            named = dict((name, variables.replace_scalar(value))
                         for name, value in named.items())
        return positional, named


class JavaArgumentResolver(object):

    def __init__(self, argspec):
        self._validator = ArgumentValidator(argspec)

    def resolve(self, arguments, variables):
        arguments = self._resolve_variables(variables, arguments)
        self._validator.validate_limits(arguments)
        return arguments, {}

    def _resolve_variables(self, variables, arguments):
        # TODO: Why/when can variables be None
        if variables:
            arguments = variables.replace_list(arguments)
        return arguments
