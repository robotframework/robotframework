#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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


class TestDefaults(object):

    def __init__(self, parent_defaults):
        self.setup = None
        self.teardown = None
        self.timeout = None
        self.force_tags = None
        self.default_tags = None
        self.test_template = None
        self.parent_defaults = parent_defaults

    # TODO change to property
    def get_force_tags(self):
        force_tags = self.force_tags or ()
        return force_tags + ((self.parent_defaults and self.parent_defaults.get_force_tags()) or ())

    def get_setup(self):
        return self.setup or (self.parent_defaults and self.parent_defaults.get_setup())

    def get_teardown(self):
        return self.teardown or (self.parent_defaults and self.parent_defaults.get_teardown())

    def get_timeout(self):
        if self.timeout:
            return self.timeout.value
        if self.parent_defaults:
            return self.parent_defaults.get_timeout()
        return None


class TestSettings(object):

    def __init__(self, defaults):
        self.defaults = defaults
        self._setup = None
        self._teardown = None
        self._timeout = None
        self._template = None
        self._tags = None

    @property
    def setup(self):
        return self._setup or self.defaults.get_setup()

    @setup.setter
    def setup(self, setup):
        self._setup = setup

    @property
    def teardown(self):
        return self._teardown or self.defaults.get_teardown()

    @teardown.setter
    def teardown(self, teardown):
        self._teardown = teardown

    @property
    def timeout(self):
        return self._timeout.value if self._timeout else self.defaults.get_timeout()

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout

    @property
    def template(self):
        if self._template:
            return self._template.value
        if self.defaults.test_template:
            return self.defaults.test_template.value
        return None

    @template.setter
    def template(self, template):
        self._template = template

    @property
    def tags(self):
        if self._tags is not None:
            tags = self._tags
        else:
            tags = self.defaults.default_tags or ()
        return tags + self.defaults.get_force_tags()

    @tags.setter
    def tags(self, tags):
        self._tags = tags
