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

    def __init__(self, argspec, resolve_named=True,
                 resolve_variables_until=None):
        self._named_resolver = NamedArgumentResolver(argspec) \
            if resolve_named else NullNamedResolver()
        self._variable_replacer = VariableReplacer(resolve_variables_until)
        self._validator = ArgumentValidator(argspec)

    def resolve(self, arguments, variables):
        positional, named = self._named_resolver.resolve(arguments)
        positional, named = self._variable_replacer.replace(positional, named,
                                                            variables)
        self._validator.validate_arguments(positional, named)
        return positional, named


class VariableReplacer(object):

    def __init__(self, resolve_until=None):
        self._resolve_until = resolve_until

    def replace(self, positional, named, variables):
        # TODO: Why/when can variables be None?
        if variables:
            positional = variables.replace_list(positional, self._resolve_until)
            named = dict((name, variables.replace_scalar(value))
                         for name, value in named.items())
        return positional, named


class NullNamedResolver(object):

    def resolve(self, arguments):
        return arguments, {}
