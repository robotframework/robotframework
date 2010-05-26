
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

from fixture import Setup, Teardown
from timeouts import TestTimeout


class DefaultValues(object):

    def __init__(self, settings, parent_default_values=None):
        self._parent = parent_default_values
        self._setup = settings.test_setup \
                      if settings.test_setup.is_set() else None
        self._teardown = settings.test_teardown \
                         if settings.test_teardown.is_set() else None
        self._timeout = settings.test_timeout \
                         if settings.test_timeout.is_set() else None
        self._force_tags = settings.force_tags.value
        self._default_tags = settings.default_tags.value

    def get_setup(self, tc_setup):
        setup = self._get_applicapble(tc_setup, self._get_setup())
        return Setup(setup.name, setup.args)

    def _get_applicapble(self, tc_value, own_value):
        if tc_value.is_set():
            return tc_value
        return own_value if own_value else tc_value

    def _get_setup(self):
        if self._setup:
            return self._setup
        return self._parent._get_setup() if self._parent else None

    def get_teardown(self, tc_teardown):
        teardown = self._get_applicapble(tc_teardown, self._get_teardown())
        return Teardown(teardown.name, teardown.args)

    def _get_teardown(self):
        if self._teardown:
            return self._teardown
        return self._parent._get_teardown() if self._parent else None

    def get_timeout(self, tc_timeout):
        timeout = self._get_applicapble(tc_timeout, self._timeout)
        return TestTimeout(timeout.value, timeout.message)

    def get_tags(self, tc_tags):
        tags = tc_tags.value if tc_tags.is_set() else self._default_tags
        return tags + self._get_force_tags()

    def _get_force_tags(self):
        if not self._parent:
            return self._force_tags
        return self._force_tags + self._parent._get_force_tags()