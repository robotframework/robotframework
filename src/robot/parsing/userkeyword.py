#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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
from robot.errors import DataError
from robot.variables import is_list_var, is_scalar_var
from robot.common import BaseHandler, UserErrorHandler

from metadata import UserKeywordMetadata
from keywords import KeywordList


def UserHandlerList(rawkeywords):
    handlers = []
    for data in rawkeywords:
        try:
            handler = UserHandler(data)
        except DataError, err:
            _report_creating_failed(data, str(err))
            handler = UserErrorHandler(data.name, str(err))
        handler = _check_for_duplicates(handlers, handler, data)
        handlers.append(handler)
    return handlers


def _check_for_duplicates(handlers, handler, data):
    for other in handlers:
        if other.name == handler.name:
            err = "Keyword '%s' defined multiple times" % handler.name
            handlers.remove(other)
            _report_creating_failed(data, err)
            return UserErrorHandler(data.name, err)
    return handler


def _report_creating_failed(data, err):
    name = utils.printable_name(data.name)
    msg = "Creating keyword '%s' failed: %s" % (name, err)
    data.report_invalid_syntax(msg)


class UserHandler(BaseHandler):

    type = 'user'

    def __init__(self, kwdata):
        self.name = utils.printable_name(kwdata.name)
        self.metadata = UserKeywordMetadata(kwdata.metadata)
        self.doc = self.metadata.get('Documentation', '')
        self.timeout = self.metadata.get('Timeout', [])
        self.keywords = KeywordList(kwdata.keywords)
        self.args, self.defaults, self.varargs \
                = self._get_arg_spec(self.metadata.get('Arguments', []))
        self.minargs = len(self.args) - len(self.defaults)
        self.maxargs = self.varargs is not None and sys.maxint or len(self.args)
        self.return_value = self.metadata.get('Return', [])

    def _get_arg_spec(self, origargs):
        """Returns argument spec in a tuple (args, defaults, varargs).

        args     - tuple of all accepted arguments
        defaults - tuple of default values
        varargs  - name of the argument accepting varargs or None

        Examples:
          ['${arg1}', '${arg2}']
            => ('${arg1}', '${arg2}'), (), None
          ['${arg1}', '${arg2}=default', '@{varargs}']
            => ('${arg1}', '${arg2}'), ('default',), '@{varargs}'
        """
        args = []
        defaults = []
        varargs = None
        for arg in origargs:
            if varargs is not None:
                raise DataError('Only last argument can be a list')
            if is_list_var(arg):
                varargs = arg
                continue   # should be last round (otherwise DataError in next)
            if arg.count('=') == 0:
                default = None
            else:
                arg, default = arg.split('=', 1)
            if len(defaults) > 0 and default is None:
                raise DataError('Non default argument after default arguments')
            if not is_scalar_var(arg):
                raise DataError("Invalid argument '%s'" % arg)
            args.append(arg)
            if default is not None:
                defaults.append(default)
        return tuple(args), tuple(defaults), varargs
