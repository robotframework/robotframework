#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

from robot import model, utils

from .message import Message


class Keyword(model.Keyword):
    __slots__ = ['status', 'starttime', 'endtime']
    message_class = Message

    def __init__(self, name='', doc='', args=None, type='kw', timeout='',
                 status='FAIL', starttime=None, endtime=None):
        model.Keyword.__init__(self, name, doc, args, type, timeout)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime

    @property
    def elapsedtime(self):
        return utils.get_elapsed_time(self.starttime, self.endtime)

    @property
    def passed(self):
        return self.status == 'PASS'
