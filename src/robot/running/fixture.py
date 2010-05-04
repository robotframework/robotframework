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

from robot import utils
from robot.errors import ExecutionFailed

from keywords import Keyword


class _Fixture(object):

    def __init__(self, kwdata=None):
        self._keyword = self._fixture_keyword(kwdata)

    def _fixture_keyword(self, kwdata):
        kwdata = utils.to_list(kwdata)
        if kwdata == []:
            return None
        return Keyword(kwdata[0], kwdata[1:], type=self.__class__.__name__.lower())

    def run(self, output, namespace):
        if self._keyword:
            try:
                self._keyword.run(output, namespace)
            except ExecutionFailed, err:
                return err
        return None

    def serialize(self, serializer):
        serializer.start_keyword(self._keyword)
        serializer.end_keyword(self._keyword)


class Setup(_Fixture): pass
class Teardown(_Fixture): pass
