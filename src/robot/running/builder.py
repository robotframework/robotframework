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

import os.path
import warnings

from robot.errors import DataError
from robot.output import LOGGER
from robot.parsing import TestData, ResourceFile as ResourceData, TEST_EXTENSIONS
from robot.running.defaults import TestDefaults
from robot.utils import abspath, is_string, normalize, unic
from robot.variables import VariableIterator

from .model import ForLoop, Keyword, ResourceFile, TestSuite


class TestSuiteBuilder(object):
    """Creates executable :class:`~robot.running.model.TestSuite` objects.

    Suites are build based on existing test data on the file system.

    See the overall documentation of the :mod:`robot.running` package for
    more information and examples.
    """

    def __init__(self, include_suites=None, warn_on_skipped='DEPRECATED',
                 extension=None, rpa=None):
        """
        :param include_suites: List of suite names to include. If ``None`` or
            an empty list, all suites are included. When executing tests
            normally, these names are specified using the ``--suite`` option.
        :param warn_on_skipped: Deprecated.
        :param extension: Limit parsing test data to only these files. Files
            are specified as an extension that is handled case-insensitively.
            Same as ``--extension`` on the command line.
        :param rpa: Explicit test execution mode. ``True`` for RPA and
           ``False`` for test automation. By default mode is got from test
           data headers and possible conflicting headers cause an error.
        """
        self.include_suites = include_suites
        self.extensions = self._get_extensions(extension)
        builder = StepBuilder()
        self._build_steps = builder.build_steps
        self._build_step = builder.build_step
        self.rpa = rpa
        self._rpa_not_given = rpa is None
        # TODO: Remove in RF 3.2.
        if warn_on_skipped != 'DEPRECATED':
            warnings.warn("Option 'warn_on_skipped' is deprecated and has no "
                          "effect.", DeprecationWarning)

    def _get_extensions(self, extension):
        if not extension:
            return None
        extensions = set(ext.lower().lstrip('.') for ext in extension.split(':'))
        if not all(ext in TEST_EXTENSIONS for ext in extensions):
            raise DataError("Invalid extension to limit parsing '%s'." % extension)
        return extensions

    def build(self, *paths):
        """
        :param paths: Paths to test data files or directories.
        :return: :class:`~robot.running.model.TestSuite` instance.
        """
        if not paths:
            raise DataError('One or more source paths required.')
        if len(paths) == 1:
            return self._parse_and_build(paths[0])
        root = TestSuite()
        for path in paths:
            root.suites.append(self._parse_and_build(path))
        root.rpa = self.rpa
        return root

    def _parse_and_build(self, path):
        suite = self._build_suite(self._parse(path))
        suite.remove_empty_suites()
        return suite

    def _parse(self, path):
        try:
            return TestData(source=abspath(path),
                            include_suites=self.include_suites,
                            extensions=self.extensions)
        except DataError as err:
            raise DataError("Parsing '%s' failed: %s" % (path, err.message))

    def _build_suite(self, data, parent_defaults=None):
        if self._rpa_not_given and data.testcase_table.is_started():
            self._set_execution_mode(data)
        self._check_deprecated_extensions(data.source)
        defaults = TestDefaults(data.setting_table, parent_defaults)
        suite = TestSuite(name=data.name,
                          source=data.source,
                          doc=unic(data.setting_table.doc),
                          metadata=self._get_metadata(data.setting_table))
        self._build_setup(suite, data.setting_table.suite_setup)
        self._build_teardown(suite, data.setting_table.suite_teardown)
        for test_data in data.testcase_table.tests:
            self._build_test(suite, test_data, defaults)
        for child in data.children:
            suite.suites.append(self._build_suite(child, defaults))
        suite.rpa = self.rpa
        ResourceFileBuilder().build(data, target=suite.resource)
        return suite

    def _set_execution_mode(self, data):
        rpa = normalize(data.testcase_table.header[0]) in ('task', 'tasks')
        if self.rpa is None:
            self.rpa = rpa
        elif self.rpa is not rpa:
            this, that = ('tasks', 'tests') if rpa else ('tests', 'tasks')
            raise DataError("Conflicting execution modes. File '%s' has %s "
                            "but files parsed earlier have %s. Fix headers "
                            "or use '--rpa' or '--norpa' options to set the "
                            "execution mode explicitly."
                            % (data.source, this, that))

    def _check_deprecated_extensions(self, source):
        if os.path.isdir(source):
            return
        ext = os.path.splitext(source)[1][1:].lower()
        if self.extensions and ext in self.extensions:
            return
        # HTML files cause deprecation warning that cannot be avoided with
        # --extension at parsing time. No need for double warning.
        if ext not in ('robot', 'html', 'htm', 'xhtml'):
            LOGGER.warn("Automatically parsing other than '*.robot' files is "
                        "deprecated. Convert '%s' to '*.robot' format or use "
                        "'--extension' to explicitly configure which files to "
                        "parse." % source)

    def _get_metadata(self, settings):
        # Must return as a list to preserve ordering
        return [(meta.name, meta.value) for meta in settings.metadata]

    def _build_test(self, suite, data, defaults):
        values = defaults.get_test_values(data)
        template = self._get_template(values.template)
        test = suite.tests.create(name=data.name,
                                  doc=unic(data.doc),
                                  tags=values.tags.value,
                                  template=template,
                                  timeout=self._get_timeout(values.timeout))
        self._build_setup(test, values.setup)
        self._build_steps(test, data, template)
        self._build_teardown(test, values.teardown)

    def _get_timeout(self, timeout):
        return (timeout.value, timeout.message) if timeout else None

    def _get_template(self, template):
        return unic(template) if template.is_active() else None

    def _build_setup(self, parent, data):
        if data.is_active():
            self._build_step(parent, data, kw_type='setup')

    def _build_teardown(self, parent, data):
        if data.is_active():
            self._build_step(parent, data, kw_type='teardown')


class ResourceFileBuilder(object):

    def __init__(self):
        builder = StepBuilder()
        self._build_steps = builder.build_steps
        self._build_step = builder.build_step

    def build(self, path_or_data, target=None):
        data, source = self._import_resource_if_needed(path_or_data)
        if not target:
            target = ResourceFile(doc=data.setting_table.doc.value, source=source)
        self._build_imports(target, data.setting_table.imports)
        self._build_variables(target, data.variable_table.variables)
        for kw_data in data.keyword_table.keywords:
            self._build_keyword(target, kw_data)
        return target

    def _import_resource_if_needed(self, path_or_data):
        if not is_string(path_or_data):
            return path_or_data, path_or_data.source
        return ResourceData(path_or_data).populate(), path_or_data

    def _build_imports(self, target, imports):
        for data in imports:
            target.imports.create(type=data.type,
                                  name=data.name,
                                  args=tuple(data.args),
                                  alias=data.alias)

    def _build_variables(self, target, variables):
        for data in variables:
            if data:
                target.variables.create(name=data.name, value=data.value)

    def _build_keyword(self, target, data):
        kw = target.keywords.create(name=data.name,
                                    args=tuple(data.args),
                                    doc=unic(data.doc),
                                    tags=tuple(data.tags),
                                    return_=tuple(data.return_),
                                    timeout=self._get_timeout(data.timeout))
        self._build_steps(kw, data)
        if data.teardown.is_active():
            self._build_step(kw, data.teardown, kw_type='teardown')

    def _get_timeout(self, timeout):
        return (timeout.value, timeout.message) if timeout else None


class StepBuilder(object):

    def build_steps(self, parent, data, template=None, kw_type='kw'):
        steps = [self._build(step, template, kw_type) for step in data.steps
                 if step and not step.is_comment()]
        parent.keywords.extend(steps)

    def build_step(self, parent, data, template=None, kw_type='kw'):
        if data and not data.is_comment():
            step = self._build(data, template, kw_type)
            parent.keywords.append(step)

    def _build(self, data, template=None, kw_type='kw'):
        if data.is_for_loop():
            return self._build_for_loop(data, template)
        if template:
            return self._build_templated_step(data, template)
        return self._build_normal_step(data, kw_type)

    def _build_for_loop(self, data, template):
        loop = ForLoop(variables=data.vars,
                       values=data.items,
                       flavor=data.flavor)
        self.build_steps(loop, data, template)
        return loop

    def _build_templated_step(self, data, template):
        args = data.as_list(include_comment=False)
        template, args = self._format_template(template, args)
        return Keyword(name=template, args=args)

    def _format_template(self, template, args):
        iterator = VariableIterator(template, identifiers='$')
        variables = len(iterator)
        if not variables or variables != len(args):
            return template, tuple(args)
        temp = []
        for before, variable, after in iterator:
            temp.extend([before, args.pop(0)])
        temp.append(after)
        return ''.join(temp), ()

    def _build_normal_step(self, data, kw_type):
        return Keyword(name=data.name,
                       args=tuple(data.args),
                       assign=tuple(data.assign),
                       type=kw_type)
