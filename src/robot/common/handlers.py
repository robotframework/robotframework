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


import sys

from robot.errors import DataError
from robot import utils


class BaseHandler:
    
    def __getattr__(self, name):
        if name == 'shortdoc':
            return self.doc != '' and self.doc.splitlines()[0] or ''
        raise AttributeError("%s does not have attribute '%s'" 
                             % (self.__class__.__name__, name))
    
    def check_arg_limits(self, args):
        if not self.minargs <= len(args) <= self.maxargs:
            self._raise_inv_args(args)
        return args

    def _raise_inv_args(self, args):
        minend = utils.plural_or_not(self.minargs)
        if self.minargs == self.maxargs:
            exptxt = "%d argument%s" % (self.minargs, minend)
        elif self.maxargs != sys.maxint:
            exptxt = "%d to %d arguments" % (self.minargs, self.maxargs)
        else:
            exptxt = "at least %d argument%s" % (self.minargs, minend)
        raise DataError("%s expected %s, got %d."
                        % (self._get_type_and_name(), exptxt, len(args)))

    def _get_type_and_name(self):
        # Overridden by InitHandlers
        return "Keyword '%s'" % self.longname

    def _tracelog_args(self, logger, args):
        argstr = ' | '.join([utils.unic(a) for a in args ])
        logger.trace('Arguments: [ %s ]' % argstr)


class UserErrorHandler:
    """Created if creating handlers fail -- running raises DataError.
    
    The idea is not to raise DataError at processing time and prevent all
    tests in affected test case file from executing. Instead UserErrorHandler
    is created and if it is ever run DataError is raised then.
    """
    type = 'error'
    
    def __init__(self, name, error):
        self.name = self.longname = name
        self.doc = self.shortdoc = ''
        self._error = error
        self.timeout = ''
        
    def run(self, *args):
        raise DataError(self._error)
