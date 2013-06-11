#  Copyright 2008-2013 Nokia Siemens Networks Oyj
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

from keyword import Keyword


class TestCase(model.TestCase):
    __slots__ = ['status', 'message', 'starttime', 'endtime']
    keyword_class = Keyword

    def __init__(self, name='', doc='', tags=None, timeout=None, status='FAIL',
                 message='', starttime=None, endtime=None):
        """Results of a single test case.
        """
        model.TestCase.__init__(self, name, doc, tags, timeout)
        self.status = status        #: String 'PASS' of 'FAIL'.
        self.message = message      #: Possible failure message.
        self.starttime = starttime  #: Test case execution start time in format ``%Y%m%d %H:%M:%S.%f``.
        self.endtime = endtime      #: Test case execution end time in format ``%Y%m%d %H:%M:%S.%f``.

    @property
    def elapsedtime(self):
        return utils.get_elapsed_time(self.starttime, self.endtime)

    @property
    def passed(self):
        return self.status == 'PASS'

    @property
    def critical(self):
        if not self.parent:
            return True
        return self.parent.criticality.test_is_critical(self)
