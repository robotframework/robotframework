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

import os

from robot.errors import DataError
from robot.variables import is_var
from robot.output import LOGGER
from robot import utils

from settings import (Documentation, Fixture, Timeout, Tags, Metadata,
                      Library, Resource, Variables, Arguments, Return)
from datareader import FromFilePopulator, FromDirectoryPopulator


def TestData(parent=None, source=None, include_suites=[]):
    if os.path.isdir(source):
        return TestDataDirectory(parent, source, include_suites)
    return TestCaseFile(parent, source)


class _TestData(object):

    def __init__(self, parent=None, source=None):
        self.parent = parent
        self.source = os.path.abspath(source) if source else None
        self.children = []

    @property
    def name(self):
        if not self.source:
            return None
        name = os.path.splitext(os.path.basename(self.source))[0]
        name = name.split('__', 1)[-1]  # Strip possible prefix
        name = name.replace('_', ' ').strip()
        return name.title() if name.islower() else name

    def report_invalid_syntax(self, table, message, level='ERROR'):
        initfile = getattr(self, 'initfile', None)
        path = os.path.join(self.source, initfile) if initfile else self.source
        LOGGER.write("Invalid syntax in file '%s' in table '%s': %s."
                     % (path, table, message), level)


class TestCaseFile(_TestData):

    def __init__(self, parent=None, source=None):
        _TestData.__init__(self, parent, source)
        self.directory = os.path.dirname(self.source) if self.source else None
        self.setting_table = TestCaseFileSettingTable(self)
        self.variable_table = VariableTable(self)
        self.testcase_table = TestCaseTable(self)
        self.keyword_table = KeywordTable(self)
        if source:
            FromFilePopulator(self).populate(source)
            self._validate()

    def _validate(self):
        if not self.testcase_table.is_started():
            raise DataError()

    def __iter__(self):
        for table in [self.setting_table, self.variable_table,
                      self.testcase_table, self.keyword_table]:
            yield table


class ResourceFile(_TestData):

    def __init__(self, source=None):
        _TestData.__init__(self, source=source)
        self.directory = os.path.dirname(self.source) if self.source else None
        self.setting_table = ResourceFileSettingTable(self)
        self.variable_table = VariableTable(self)
        self.testcase_table = TestCaseTableNotAllowed('resource file')
        self.keyword_table = KeywordTable(self)
        if self.source:
            FromFilePopulator(self).populate(source)
            self._report_status()

    def __iter__(self):
        for table in [self.setting_table, self.variable_table,
                      self.keyword_table]:
            yield table

    def _report_status(self):
        if self.setting_table or self.variable_table or self.keyword_table:
            LOGGER.info("Imported resource file '%s' (%d keywords)"
                        % (self.source, len(self.keyword_table.keywords)))
        else:
            LOGGER.warn("Imported resource file '%s' is empty." % self.source)


class TestDataDirectory(_TestData):

    def __init__(self, parent=None, source=None, include_suites=[]):
        _TestData.__init__(self, parent, source)
        self.directory = self.source
        self.initfile = None
        self.setting_table = InitFileSettingTable(self)
        self.variable_table = VariableTable(self)
        self.testcase_table = TestCaseTableNotAllowed('test suite init file')
        self.keyword_table = KeywordTable(self)
        if self.source:
            FromDirectoryPopulator().populate(self.source, self, include_suites)

    def add_child(self, path, include_suites):
        self.children.append(TestData(parent=self,source=path, 
                                      include_suites=include_suites))

    def __iter__(self):
        for table in [self.setting_table, self.variable_table,
                      self.keyword_table]:
            yield table


class _Table(object):

    def __init__(self, parent):
        self.parent = parent
        self.header = None

    def set_header(self, header):
        self.header = header

    @property
    def name(self):
        return self.header[0]

    @property
    def source(self):
        return self.parent.source

    @property
    def directory(self):
        return self.parent.directory

    def report_invalid_syntax(self, message, level='ERROR'):
        self.parent.report_invalid_syntax(self.name, message, level)


class _WithSettings(object):

    def get_setter(self, setting_name):
        if setting_name in self._setters:
            return self._setters[setting_name]
        self.report_invalid_syntax("Non-existing setting '%s'" % setting_name)

    def is_setting(self, setting_name):
        return setting_name in self._setters


class _SettingTable(_Table, _WithSettings):

    def __init__(self, parent):
        _Table.__init__(self, parent)
        self.doc = Documentation(self)
        self.suite_setup = Fixture(self)
        self.suite_teardown = Fixture(self)
        self.test_setup = Fixture(self)
        self.test_teardown = Fixture(self)
        self.test_timeout = Timeout(self)
        self.force_tags = Tags(self)
        self.default_tags = Tags(self)
        self.metadata = []
        self.imports = []
        self._setters = self._get_setters()

    def _get_adder(self, adder_method):
        def adder(value, comment):
            name = value[0] if value else ''
            adder_method(name, value[1:], comment)
        return adder

    def add_metadata(self, name, value='', comment=None):
        self.metadata.append(Metadata(self, name, value, comment))
        return self.metadata[-1]

    def add_library(self, name, args=None, comment=None):
        self.imports.append(Library(self, name, args, comment=comment))
        return self.imports[-1]

    def add_resource(self, name, invalid_args=None, comment=None):
        self.imports.append(Resource(self, name, invalid_args, comment=comment))
        return self.imports[-1]

    def add_variables(self, name, args=None, comment=None):
        self.imports.append(Variables(self, name, args, comment=comment))
        return self.imports[-1]

    def __iter__(self):
        for setting in [self.doc, self.suite_setup, self.suite_teardown,
                        self.test_setup, self.test_teardown, self.test_timeout,
                        self.force_tags, self.default_tags] \
                        + self.metadata + self.imports:
            yield setting

    def __nonzero__(self):
        return any(setting.is_set() for setting in self)


class TestCaseFileSettingTable(_SettingTable):

    def _get_setters(self):
        return utils.NormalizedDict({'Documentation': self.doc.set,
                                     'Document': self.doc.set,
                                     'Suite Setup': self.suite_setup.set,
                                     'Suite Precondition': self.suite_setup.set,
                                     'Suite Teardown': self.suite_teardown.set,
                                     'Suite Postcondition': self.suite_teardown.set,
                                     'Test Setup': self.test_setup.set,
                                     'Test Precondition': self.test_setup.set,
                                     'Test Teardown': self.test_teardown.set,
                                     'Test Postcondition': self.test_teardown.set,
                                     'Force Tags': self.force_tags.set,
                                     'Default Tags': self.default_tags.set,
                                     'Test Timeout': self.test_timeout.set,
                                     'Library': self._get_adder(self.add_library),
                                     'Resource': self._get_adder(self.add_resource),
                                     'Variables': self._get_adder(self.add_variables),
                                     'Metadata': self._get_adder(self.add_metadata)})


class ResourceFileSettingTable(_SettingTable):
    def _get_setters(self):
        return utils.NormalizedDict({'Documentation': self.doc.set,
                                     'Document': self.doc.set,
                                     'Library': self._get_adder(self.add_library),
                                     'Resource': self._get_adder(self.add_resource),
                                     'Variables': self._get_adder(self.add_variables)})


class InitFileSettingTable(_SettingTable):
    def _get_setters(self):
        return utils.NormalizedDict({'Documentation': self.doc.set,
                                     'Document': self.doc.set,
                                     'Suite Setup': self.suite_setup.set,
                                     'Suite Precondition': self.suite_setup.set,
                                     'Suite Teardown': self.suite_teardown.set,
                                     'Suite Postcondition': self.suite_teardown.set,
                                     'Test Setup': self.test_setup.set,
                                     'Test Precondition': self.test_setup.set,
                                     'Test Teardown': self.test_teardown.set,
                                     'Test Postcondition': self.test_teardown.set,
                                     'Force Tags': self.force_tags.set,
                                     'Library': self._get_adder(self.add_library),
                                     'Resource': self._get_adder(self.add_resource),
                                     'Variables': self._get_adder(self.add_variables),
                                     'Metadata': self._get_adder(self.add_metadata)})


class VariableTable(_Table):

    def __init__(self, parent):
        _Table.__init__(self, parent)
        self.variables = []

    def add(self, name, value, comment=None):
        self.variables.append(Variable(name, value, comment))

    def __iter__(self):
        return iter(self.variables)

    def __nonzero__(self):
        return bool(self.variables)


class TestCaseTable(_Table):

    def __init__(self, parent):
        _Table.__init__(self, parent)
        self.tests = []

    def add(self, name):
        self.tests.append(TestCase(self, name))
        return self.tests[-1]

    def __iter__(self):
        return iter(self.tests)

    def __nonzero__(self):
        return bool(self.tests)

    def is_started(self):
        return bool(self.header)


class KeywordTable(_Table):

    def __init__(self, parent):
        _Table.__init__(self, parent)
        self.keywords = []

    def add(self, name):
        self.keywords.append(UserKeyword(self, name))
        return self.keywords[-1]

    def __iter__(self):
        return iter(self.keywords)

    def __nonzero__(self):
        return bool(self.keywords)


class TestCaseTableNotAllowed(object):

    def __init__(self, where):
        self.message = 'Test case table not allowed in %s.' % where

    def __getattr__(self, name):
        raise DataError(self.message)

    def __nonzero__(self):
        return False

    def __iter__(self):
        return iter([])


class Variable(object):

    def __init__(self, name, value, comment=None):
        self.name = name.rstrip('= ')
        if name.startswith('$') and value == []:
            value = ''
        if isinstance(value, basestring):
            value = [value]  # Need to support scalar lists until RF 2.6
        self.value = value
        self.comment = comment


class _WithSteps(object):

    def add_step(self, content, comment=None):
        self.steps.append(Step(content, comment))
        return self.steps[-1]


class TestCase(_WithSteps, _WithSettings):

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.doc = Documentation(self)
        self.tags = Tags(self)
        self.setup = Fixture(self)
        self.teardown = Fixture(self)
        self.timeout = Timeout(self)
        self.steps = []
        self._setters = self._get_setters()

    def _get_setters(self):
        return utils.NormalizedDict({'Documentation': self.doc.set,
                                     'Document': self.doc.set,
                                     'Setup': self.setup.set,
                                     'Precondition': self.setup.set,
                                     'Teardown': self.teardown.set,
                                     'Postcondition': self.teardown.set,
                                     'Tags': self.tags.set,
                                     'Timeout': self.timeout.set})

    @property
    def source(self):
        return self.parent.source

    @property
    def directory(self):
        return self.parent.directory

    def add_for_loop(self, data):
        self.steps.append(ForLoop(data))
        return self.steps[-1]

    def report_invalid_syntax(self, message, level='ERROR'):
        type = 'test case' if isinstance(self, TestCase) else 'keyword'
        message = "Invalid syntax in %s '%s': %s" % (type, self.name, message)
        self.parent.report_invalid_syntax(message, level)


class UserKeyword(TestCase):

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.doc = Documentation(self)
        self.args = Arguments(self)
        self.return_ = Return(self)
        self.timeout = Timeout(self)
        self.steps = []
        self._setters = self._get_setters()

    def _get_setters(self):
        return utils.NormalizedDict({'Documentation': self.doc.set,
                                     'Document': self.doc.set,
                                     'Arguments': self.args.set,
                                     'Return': self.return_.set,
                                     'Timeout': self.timeout.set})


class ForLoop(_WithSteps):

    def __init__(self, content):
        self.range, index = self._get_range_and_index(content)
        self.vars = content[:index]
        self.items = content[index+1:]
        self.steps = []

    def _get_range_and_index(self, content):
        for index, item in enumerate(content):
            if item.upper() in ['IN', 'IN RANGE']:
                return item.upper() == 'IN RANGE', index
        return False, len(content)

    def is_comment(self):
        return False

    def is_for_loop(self):
        return True


class Step(object):

    def __init__(self, content, comment=None):
        self.assign = self._get_assigned_vars(content)
        try:
            self.keyword = content[len(self.assign)]
        except IndexError:
            self.keyword = ''
        self.args = content[len(self.assign)+1:]
        self.comment = comment

    def _get_assigned_vars(self, content):
        vars = []
        for item in content:
            item = item.rstrip('= ')
            if not is_var(item):
                break
            vars.append(item)
        return vars

    def is_comment(self):
        return not (self.assign or self.keyword or self.args)

    def is_for_loop(self):
        return False
