#  Copyright 2008-2015 Nokia Solutions and Networks
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

    def __init__(self, settings, parent=None):
        self.setup = settings.test_setup
        self.teardown = settings.test_teardown
        self.timeout = settings.test_timeout
        self.force_tags = settings.force_tags
        self.default_tags = settings.default_tags
        self.template = settings.test_template
        if parent:
            self.setup = self.setup or parent.setup
            self.teardown = self.teardown or parent.teardown
            self.timeout = self.timeout or parent.timeout
            self.force_tags += parent.force_tags

    def get_test_values(self, test):
        return TestValues(test, self)


class TestValues(object):

    def __init__(self, test, defaults):
        self.setup = test.setup or defaults.setup
        self.teardown = test.teardown or defaults.teardown
        self.timeout = test.timeout or defaults.timeout
        self.template = test.template or defaults.template
        self.tags = (test.tags or defaults.default_tags) + defaults.force_tags
