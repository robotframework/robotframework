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

NOTSET = object()


class TestDefaults(object):

    def __init__(self, parent=None):
        self.parent = parent
        self._setup = {}
        self._teardown = {}
        self._force_tags = ()
        self.default_tags = ()
        self.template = None
        self._timeout = None

    @property
    def setup(self):
        if self._setup:
            return self._setup
        if self.parent:
            return self.parent.setup
        return {}

    @setup.setter
    def setup(self, setup):
        self._setup = setup

    @property
    def teardown(self):
        if self._teardown:
            return self._teardown
        if self.parent:
            return self.parent.teardown
        return {}

    @teardown.setter
    def teardown(self, teardown):
        self._teardown = teardown

    @property
    def force_tags(self):
        parent_force_tags = self.parent.force_tags if self.parent else ()
        return self._force_tags + parent_force_tags

    @force_tags.setter
    def force_tags(self, force_tags):
        self._force_tags = force_tags

    @property
    def timeout(self):
        if self._timeout:
            return self._timeout
        if self.parent:
            return self.parent.timeout
        return None

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout


class TestSettings(object):

    def __init__(self, defaults):
        self.defaults = defaults
        self._setup = NOTSET
        self._teardown = NOTSET
        self._timeout = NOTSET
        self._template = NOTSET
        self._tags = NOTSET

    @property
    def setup(self):
        if self._setup is NOTSET:
            return self.defaults.setup
        return self._setup

    @setup.setter
    def setup(self, setup):
        self._setup = setup

    @property
    def teardown(self):
        if self._teardown is NOTSET:
            return self.defaults.teardown
        return self._teardown

    @teardown.setter
    def teardown(self, teardown):
        self._teardown = teardown

    @property
    def timeout(self):
        if self._timeout is NOTSET:
            return self.defaults.timeout
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout

    @property
    def template(self):
        if self._template is NOTSET:
            return self.defaults.template
        return self._template

    @template.setter
    def template(self, template):
        self._template = template

    @property
    def tags(self):
        if self._tags is NOTSET:
            tags = self.defaults.default_tags
        else:
            tags = self._tags
        return tags + self.defaults.force_tags

    @tags.setter
    def tags(self, tags):
        self._tags = tags
