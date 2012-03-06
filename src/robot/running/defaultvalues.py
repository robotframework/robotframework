
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

from fixture import Setup, Teardown
from timeouts import TestTimeout


class DefaultValues(object):

    def __init__(self, settings, parent_default_values=None):
        self._parent = parent_default_values
        self._setup = settings.test_setup
        self._teardown = settings.test_teardown
        self._timeout = settings.test_timeout
        self._force_tags = settings.force_tags
        self._default_tags = settings.default_tags
        self._test_template = settings.test_template

    def get_setup(self, tc_setup):
        setup = tc_setup if tc_setup.is_set() else self._get_default_setup()
        return Setup(setup.name, setup.args)

    def _get_default_setup(self):
        if self._setup.is_set() or not self._parent:
            return self._setup
        return self._parent._get_default_setup()

    def get_teardown(self, tc_teardown):
        td = tc_teardown if tc_teardown.is_set() else self._get_default_teardown()
        return Teardown(td.name, td.args)

    def _get_default_teardown(self):
        if self._teardown.is_set() or not self._parent:
            return self._teardown
        return self._parent._get_default_teardown()

    def get_timeout(self, tc_timeout):
        timeout = tc_timeout if tc_timeout.is_set() else self._get_default_timeout()
        return TestTimeout(timeout.value, timeout.message)

    def _get_default_timeout(self):
        if self._timeout.is_set() or not self._parent:
            return self._timeout
        return self._parent._get_default_timeout()

    def get_tags(self, tc_tags):
        tags = tc_tags if tc_tags.is_set() else self._default_tags
        return (tags + self._get_force_tags()).value

    def _get_force_tags(self):
        if not self._parent:
            return self._force_tags
        return self._force_tags + self._parent._get_force_tags()

    def get_template(self, template):
        tmpl = (template if template.is_set() else self._test_template).value
        return tmpl if tmpl and tmpl.upper() != 'NONE' else None
