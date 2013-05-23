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
from robot.errors import ExecutionPassed


class BaseKeyword:

    def __init__(self, name='', args=None, doc='', timeout='', type='kw'):
        self.name = name
        self.args = args or []
        self.doc = doc
        self.timeout = timeout
        self.type = type
        self.message = ''
        self.status = 'NOT_RUN'

    @property
    def passed(self):
        return self.status == 'PASS'

    def serialize(self, serializer):
        serializer.start_keyword(self)
        serializer.end_keyword(self)

    def _get_status(self, error):
        if not error:
            return 'PASS'
        if isinstance(error, ExecutionPassed) and not error.earlier_failures:
            return 'PASS'
        return 'FAIL'
