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
from robot.running.timeouts import TestTimeout

from .model import TestSuite, ForLoop


class TestSuiteBuilder(object):

    def __init__(self):
        pass

    def build(self, *paths):
        if len(paths) == 1:
            return self._build_suite(TestData(source=paths[0]))
        root = TestSuite()
        for path in paths:
            root.suites.append(self._build_suite(TestData(source=path)))
        return root

    def _build_suite(self, data, parent_defaults=None):
        defaults = TestDefaults(data.setting_table, parent_defaults)
        suite = TestSuite(name=data.name,
                          source=data.source,
                          doc=unicode(data.setting_table.doc),
                          metadata=self._get_metadata(data.setting_table))
        for import_data in data.setting_table.imports:
            self._create_import(suite, import_data)
        self._create_step(suite, data.setting_table.suite_setup, 'setup')
        self._create_step(suite, data.setting_table.suite_teardown, 'teardown')
        for var_data in data.variable_table.variables:
            self._create_variable(suite, var_data)
        for uk_data in data.keyword_table.keywords:
            self._create_user_keyword(suite, uk_data)
        for test_data in data.testcase_table.tests:
            self._create_test(suite, test_data, defaults)
        for child in data.children:
            suite.suites.append(self._build_suite(child, defaults))
        return suite

    def _get_metadata(self, settings):
        return dict((meta.name, meta.value) for meta in settings.metadata)

    def _create_import(self, suite, data):
        suite.imports.create(type=data.type,
                             name=data.name,
                             args=tuple(data.args),
                             alias=data.alias)

    def _create_test(self, suite, data, defaults):
        values = defaults.get_test_values(data)
        test = suite.tests.create(name=data.name,
                                  doc=unicode(data.doc),
                                  tags=values.tags.value,
                                  timeout=TestTimeout(values.timeout.value,
                                                      values.timeout.message))
        self._create_step(test, values.setup, 'setup')
        for step_data in data.steps:
            self._create_step(test, step_data)
        self._create_step(test, values.teardown, 'teardown')

    def _create_user_keyword(self, suite, data):
        # TODO: Tests and uks have inconsistent timeout types
        uk = suite.user_keywords.create(name=data.name,
                                        args=tuple(data.args),
                                        doc=unicode(data.doc),
                                        return_=tuple(data.return_),
                                        timeout=data.timeout)
        for step_data in data.steps:
            self._create_step(uk, step_data)

    def _create_variable(self, suite, data):
        if not data:
            return
        if data.name.startswith('$'):
            value = data.value[0]
        else:
            value = data.value
        suite.variables.create(name=data.name, value=value)

    def _create_step(self, parent, data, type='kw'):
        if not data or data.is_comment():
            return
        if data.is_for_loop():
            self._create_for_loop(parent, data)
        else:
            parent.keywords.create(name=data.keyword,
                                   args=tuple(data.args),
                                   assign=tuple(data.assign),
                                   type=type)

    def _create_for_loop(self, parent, data):
        loop = parent.keywords.append(ForLoop(vars=data.vars,
                                              items=data.items,
                                              range=data.range))
        for step in data.steps:
            self._create_step(loop, step)
