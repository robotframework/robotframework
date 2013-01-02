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

from robot.errors import ExecutionFailed, DataError

from .keywords import Keyword


class _Fixture(object):

    def __init__(self, name, args):
        self.name = name or ''
        self.args = args
        self._keyword = None

    def replace_variables(self, variables, errors):
        if self.name:
            try:
                self.name = variables.replace_string(self.name)
            except DataError, err:
                errors.append('Replacing variables from %s failed: %s'
                              % (self.__class__.__name__, unicode(err)))
            if self.name.upper() != 'NONE':
                self._keyword = Keyword(self.name, self.args,
                                        type=type(self).__name__.lower())

    def run(self, context):
        if self._keyword:
            try:
                self._keyword.run(context)
            except ExecutionFailed, err:
                return err

    def serialize(self, serializer):
        if self._keyword:
            serializer.start_keyword(self._keyword)
            serializer.end_keyword(self._keyword)


class Setup(_Fixture):
    pass


class Teardown(_Fixture):
    pass
