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

from robot.errors import DataError
from robot.variables import is_list_var
from robot import utils


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

    # TODO: Proof-read error messages
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
