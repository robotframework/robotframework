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

from robot.errors import DataError
from robot.parsing import TestData
from robot.running.defaults import TestDefaults
from robot.utils import abspath
from robot.variables import VariableIterator

from .model import TestSuite, ForLoop


class TestSuiteBuilder(object):

    def __init__(self, include_suites=None, warn_on_skipped=False, include_empty_suites=False):
        """Create programmatically executable
        :class:`~robot.running.model.TestSuite` objects based on existing data
        on the file system.

        See example of usage in :mod:`.running` package.
        """
        self.include_suites = include_suites
        self.warn_on_skipped = warn_on_skipped
        self.include_empty_suites = include_empty_suites

    def build(self, *paths):
        if not paths:
            raise DataError('One or more source paths required.')
        if len(paths) == 1:
            return self._build_and_check_if_empty(paths[0])
        root = TestSuite()
        for path in paths:
            root.suites.append(self._build_and_check_if_empty(path))
        return root

    def _build_and_check_if_empty(self, path):
        builded = self._build_suite(self._parse(path))
        if not self._empty_suites_allowed and not builded.test_count:
                raise DataError("Suite '%s' contains no tests." % builded.name)
        builded.remove_empty_suites()
        return builded

    @property
    def _empty_suites_allowed(self):
        return self.include_empty_suites or self.include_suites

    def _parse(self, path):
        try:
            return TestData(source=abspath(path),
                            include_suites=self.include_suites,
                            warn_on_skipped=self.warn_on_skipped)
        except DataError, err:
            raise DataError("Parsing '%s' failed: %s" % (path, unicode(err)))

    def _build_suite(self, data, parent_defaults=None):
        defaults = TestDefaults(data.setting_table, parent_defaults)
        suite = TestSuite(name=data.name,
                          source=data.source,
                          doc=unicode(data.setting_table.doc),
                          metadata=self._get_metadata(data.setting_table))
        for import_data in data.setting_table.imports:
            self._create_import(suite, import_data)
        self._create_setup(suite, data.setting_table.suite_setup)
        self._create_teardown(suite, data.setting_table.suite_teardown)
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
        # Must return as a list to preserve ordering
        return [(meta.name, meta.value) for meta in settings.metadata]

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
                                  template=self._get_template(values.template),
                                  timeout=self._get_timeout(values.timeout))
        self._create_setup(test, values.setup)
        for step_data in data.steps:
            self._create_step(test, step_data, template=values.template)
        self._create_teardown(test, values.teardown)

    def _get_timeout(self, timeout):
        return (timeout.value, timeout.message) if timeout else None

    def _get_template(self, template):
        return unicode(template) if template.is_active() else None

    def _create_user_keyword(self, suite, data):
        uk = suite.user_keywords.create(name=data.name,
                                        args=tuple(data.args),
                                        doc=unicode(data.doc),
                                        return_=tuple(data.return_),
                                        timeout=data.timeout,
                                        teardown=data.teardown)
        for step_data in data.steps:
            self._create_step(uk, step_data)

    def _create_variable(self, suite, data):
        if data:
            suite.variables.create(name=data.name, value=data.value)

    def _create_setup(self, parent, data):
        if data.is_active():
            self._create_step(parent, data, kw_type='setup')

    def _create_teardown(self, parent, data):
        if data.is_active():
            self._create_step(parent, data, kw_type='teardown')

    def _create_step(self, parent, data, template=None, kw_type='kw'):
        if not data or data.is_comment():
            return
        if data.is_for_loop():
            self._create_for_loop(parent, data, template)
        elif template and template.is_active():
            self._create_templated(parent, data, template)
        else:
            parent.keywords.create(name=data.keyword,
                                   args=tuple(data.args),
                                   assign=tuple(data.assign),
                                   type=kw_type)

    def _create_templated(self, parent, data, template):
        args = data.as_list(include_comment=False)
        template, args = self._format_template(unicode(template), args)
        parent.keywords.create(name=template, args=tuple(args))

    def _format_template(self, template, args):
        iterator = VariableIterator(template, identifiers='$')
        variables = len(iterator)
        if not variables or variables != len(args):
            return template, args
        temp = []
        for before, variable, after in iterator:
            temp.extend([before, args.pop(0)])
        temp.append(after)
        return ''.join(temp), ()

    def _create_for_loop(self, parent, data, template):
        loop = parent.keywords.append(ForLoop(vars=data.vars,
                                              items=data.items,
                                              range=data.range))
        for step in data.steps:
            self._create_step(loop, step, template=template)
