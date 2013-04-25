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

from robot import utils


class ArgumentSpec(object):

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
