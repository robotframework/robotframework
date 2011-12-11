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

try:
    from timeoutsignaling import TimeoutWithSignaling as _Timeout
except ImportError:
    import os
    if os.name == 'nt':
        from timeoutwin import TimeoutWithTimerThrowingException as _Timeout
    else:
        from timeoutthread import TimeoutWithThread as _Timeout


class TestTimeout(_Timeout):
    _keyword_timeouted = False

    def set_keyword_timeout(self, timeout_occurred):
        self._keyword_timeouted = self._keyword_timeouted or timeout_occurred

    def any_timeout_occurred(self):
        return self.timed_out() or self._keyword_timeouted


class KeywordTimeout(_Timeout):
    pass
