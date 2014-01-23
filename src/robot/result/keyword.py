#  Copyright 2008-2014 Nokia Solutions and Networks
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
    """Results of a single keyword."""
    __slots__ = ['status', 'starttime', 'endtime', 'message']
    message_class = Message

    def __init__(self, name='', doc='', args=(), type='kw', timeout='',
                 status='FAIL', starttime=None, endtime=None):
        model.Keyword.__init__(self, name, doc, args, type, timeout)
        #: String 'PASS' of 'FAIL'.
        self.status = status
        #: Keyword execution start time in format ``%Y%m%d %H:%M:%S.%f``.
        self.starttime = starttime
        #: Keyword execution end time in format ``%Y%m%d %H:%M:%S.%f``.
        self.endtime = endtime
        #: Keyword status message. Used only with suite teardowns.
        self.message = ''

    @property
    def elapsedtime(self):
        """Elapsed execution time of the keyword in milliseconds."""
        return utils.get_elapsed_time(self.starttime, self.endtime)

    @property
    def passed(self):
        """``True`` if the keyword did pass, ``False`` otherwise."""
        return self.status == 'PASS'
