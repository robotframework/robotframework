#  Copyright 2008 Nokia Siemens Networks Oyj
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


import os

from robot.common import BaseHandler, BaseLibrary, UserErrorHandler
from robot.errors import DataError, ExecutionFailed
from robot.variables import is_list_var
from robot import utils

from keywords import KeywordFactory
from timeouts import KeywordTimeout


def PublicUserLibrary(path):
    """Create a user library instance from given resource file."""
    from robot.parsing import ResourceFile
    
    resource = ResourceFile(path)
    ret = UserLibrary(resource.user_keywords, path)
    ret.doc = resource.doc
    return ret


class UserLibrary(BaseLibrary):

    def __init__(self, handlerdata, path=None):
        if path is not None:
            self.name = os.path.splitext(os.path.basename(path))[0]
        else:
            self.name = None
        self.handlers = utils.NormalizedDict(ignore=['_'])
        for handler in handlerdata:
            if handler.type != 'error':
                handler = UserHandler(handler, self.name)
            if self.handlers.has_key(handler.name):
                err = "Keyword '%s' defined multiple times" % handler.name
                handler = UserErrorHandler(handler.name, err)
            self.handlers[handler.name] = handler


class UserHandler(BaseHandler):

    type = 'user'

    def __init__(self, handlerdata, libname):
        self.name = utils.printable_name(handlerdata.name)
        if libname is None: 
            self.longname = self.name
        else:
            self.longname = '%s.%s' % (libname, self.name)
        self._set_variable_dependent_metadata(handlerdata.metadata)
        self.keywords = [ KeywordFactory(kw) for kw in handlerdata.keywords ]
        self.args = handlerdata.args
        self.defaults = handlerdata.defaults
        self.varargs = handlerdata.varargs
        self.minargs = handlerdata.minargs
        self.maxargs = handlerdata.maxargs
        self.return_value = handlerdata.return_value
        
    def _set_variable_dependent_metadata(self, metadata):
        self._doc = metadata.get('Documentation', '')
        self.doc = utils.unescape(self._doc)
        self._timeout = metadata.get('Timeout', [])
        self.timeout = [ utils.unescape(item) for item in self._timeout ]
    
    def init_user_keyword(self, varz):
        self._errors = []
        self.doc = varz.replace_meta('Documentation', self._doc, self._errors)
        timeout = varz.replace_meta('Timeout', self._timeout, self._errors)
        self.timeout = KeywordTimeout(*timeout)

    def run(self, output, namespace, args):
        namespace.start_user_keyword(self)
        args = namespace.variables.replace_list(args)
        self._tracelog_args(output, args)
        self.check_arg_limits(args)
        if len(args) < len(self.args):
            args += self._get_defaults(args, namespace.variables)
        for name, value in zip(self.args, args):
            namespace.variables[name] = value
        if self.varargs is not None:
            namespace.variables[self.varargs] = self._get_varargs(args)
        self._verify_keyword_is_valid()
        self.timeout.start()
        for kw in self.keywords:
            try:
                kw.run(output, namespace)
            except ExecutionFailed:
                namespace.end_user_keyword()
                raise
        ret = self._get_return_value(namespace.variables)
        namespace.end_user_keyword()
        output.trace('Return: %s' % utils.unic(ret))
        return ret

    def _verify_keyword_is_valid(self):
        if self._errors:
            raise DataError('User keyword initialization failed:\n%s' 
                            % '\n'.join(self._errors)) 
        if not (self.keywords or self.return_value):
            raise DataError("User keyword contains no keywords")

    def _get_return_value(self, variables):
        if not self.return_value:
            return None
        ret = variables.replace_list(self.return_value)
        if len(ret) != 1 or is_list_var(self.return_value[0]):
            return ret
        return ret[0]
                
    def _get_defaults(self, args, variables):
        """Returns as many default values as needed"""
        defaults_needed = len(self.args) - len(args)
        defaults = self.defaults[len(self.defaults)-defaults_needed:]
        return tuple(variables.replace_list(defaults))
    
    def _get_varargs(self, args):
        """Returns args leftoever from argspec and thus belonging to varargs"""
        vararg_count = len(args) - len(self.args)
        varargs = args[len(args)-vararg_count:]
        return varargs  # Variables already replaced
