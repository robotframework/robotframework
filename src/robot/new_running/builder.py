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

from robot.new_running.defaults import TestDefaults
from robot.parsing import TestData

from .model import TestSuite


class TestSuiteBuilder(object):

    def __init__(self):
        pass

    def build(self, *paths):
        if len(paths) == 1:
            return self._build(TestData(source=paths[0]))
        root = TestSuite()
        for path in paths:
            root.suites.append(self._build(TestData(source=path)))
        return root

    def _build(self, data, parent_defaults=None):
        defaults = TestDefaults(data.setting_table, parent_defaults)
        suite = TestSuite(name=data.name,
                          source=data.source,
                          doc=data.setting_table.doc.value)
        for imp in data.setting_table.imports:
            suite.imports.create(type=imp.type,
                                 name=imp.name,
                                 args=tuple(imp.args),
                                 alias=imp.alias)
        self._create_fixture(suite, data.setting_table.suite_setup, 'setup')
        self._create_fixture(suite, data.setting_table.suite_teardown, 'teardown')
        for var_data in data.variable_table.variables:
            self._create_variable(suite, var_data)
        for uk_data in data.keyword_table.keywords:
            self._create_uk(suite, uk_data)
        for test_data in data.testcase_table.tests:
            self._create_test(suite, test_data, defaults)
        for child in data.children:
            suite.suites.append(self._build(child, parent_defaults=defaults))
        return suite

    def _create_test(self, suite, test_data, defaults):
        test_values = defaults.get_test_values(test_data)
        test = suite.tests.create(name=test_data.name,
                                  doc=test_data.doc.value,
                                  tags=test_values.tags.value)
        self._create_fixture(test, test_values.setup, 'setup')
        for step_data in test_data.steps:
            self._create_step(test, step_data)
        self._create_fixture(test, test_values.teardown, 'teardown')

    def _create_uk(self, suite, uk_data):
        uk = suite.user_keywords.create(name=uk_data.name,
                                        args=tuple(uk_data.args))
        for step_data in uk_data.steps:
            self._create_step(uk, step_data)

    def _create_variable(self, suite, var_data):
        if var_data.name.startswith('$'):
            value = var_data.value[0]
        else:
            value = var_data.value
        suite.variables.create(name=var_data.name,
                               value=value)

    def _create_fixture(self, target, element, fixture_type):
        if element:
            target.keywords.create(type=fixture_type,
                                   name=element.name,
                                   args=tuple(element.args))

    def _create_step(self, parent, step_data):
        parent.keywords.create(name=step_data.keyword,
                               args=tuple(step_data.args),
                               assign=tuple(step_data.assign))

    def _get_tags(self, test):
        # FIXME: get tags from a context
        settings = test.parent.parent.setting_table
        tags = test.tags.value
        defaults = settings.default_tags.value or []
        forced = settings.force_tags.value or []
        if tags is None:
            tags = defaults
        return tags + forced
