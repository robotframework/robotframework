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


from robot import utils
from robot.errors import ExecutionFailed

from keywords import Keyword


class _Fixture:

    def __init__(self, kwdata):
        if kwdata:
            kwtype=self.name.split()[-1].lower()
            self._keyword = Keyword(kwdata[0], kwdata[1:], type=kwtype)
        else:
            self._keyword = None

    def run(self, output, namespace, *errors):
        try:
            if self._is_executed(*errors):
                self._keyword.run(output, namespace)
        except ExecutionFailed:
            return '%s failed:\n%s' % (self.name, utils.get_error_message())

    def serialize(self, serializer):
        if self._is_executed():
            self._keyword.serialize(serializer)

    def _is_executed(self, *errors):
        for err in errors:
            if err is not None:
                return False
        return self._keyword is not None


class SuiteSetup(_Fixture):
    name = 'Suite setup'

class SuiteTeardown(_Fixture):
    name = 'Suite teardown'

class TestSetup(_Fixture):
    name = 'Setup'

class TestTeardown(_Fixture):
    name = 'Teardown'


