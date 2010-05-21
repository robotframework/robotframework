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

from settings import (Documentation, Fixture, Timeout, Tags, Metadata,
                      Library, Resource, Variables, Arguments, Return)
from datareader import FromFilePopulator, FromDirectoryPopulator


def TestData(path):
    if os.path.isdir(path):
        return TestDataDirectory(path)
    return TestCaseFile(path)


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
        name = name.replace('_', ' ').strip()
        return name.title() if name.islower() else name

    def report_invalid_syntax(self, table, message, level='ERROR'):
        initfile = getattr(self, 'initfile', None)
        path = os.path.join(self.source, initfile) if initfile else self.source
        LOGGER.write("Invalid syntax in file '%s' in table '%s': %s"
                     % (path, table, message), level)


class TestCaseFile(_TestData):

    def __init__(self, parent=None, source=None):
        _TestData.__init__(self, source)
        self.directory = os.path.dirname(self.source) if self.source else None
        self.setting_table = SettingTable(self)
        self.variable_table = VariableTable(self)
        self.testcase_table = TestCaseTable(self)
        self.keyword_table = KeywordTable(self)
        if source:
            FromFilePopulator(self).populate(source)

    def __iter__(self):
        for table in [self.setting_table, self.variable_table,
                      self.testcase_table, self.keyword_table]:
            yield table


class ResourceFile(_TestData):

    def __init__(self, source=None):
        _TestData.__init__(self, source=source)
        self.directory = os.path.dirname(self.source) if self.source else None
        self.setting_table = SettingTable(self)
        self.variable_table = VariableTable(self)
        self.testcase_table = TestCaseTableNotAllowed('resource file')
        self.keyword_table = KeywordTable(self)
        if self.source:
            FromFilePopulator(self).populate(source)

    def __iter__(self):
        for table in [self.setting_table, self.variable_table,
                      self.keyword_table]:
            yield table


class TestDataDirectory(_TestData):

    def __init__(self, parent=None, source=None):
        _TestData.__init__(self, parent, source)
        self.directory = self.source
        self.initfile = None
        self.setting_table = SettingTable(self)
        self.variable_table = VariableTable(self)
        self.testcase_table = TestCaseTableNotAllowed('test suite init file')
        self.keyword_table = KeywordTable(self)
        if self.source:
            FromDirectoryPopulator().populate(self.source, self)

    def add_child(self, path):
        self.children.append(TestData(parent=self,source=path))

    def __iter__(self):
        for table in [self.setting_table, self.variable_table,
                      self.keyword_table]:
            yield table


class _Table(object):

    def __init__(self, parent):
        self.parent = parent

    @property
    def source(self):
        return self.parent.source

    @property
    def directory(self):
        return self.parent.directory

    def report_invalid_syntax(self, message, level='ERROR'):
        # TODO: Use the real table name here when headers are available
        table = type(self).__name__.replace('Table', '')
        self.parent.report_invalid_syntax(table, message, level)


class SettingTable(_Table):

    def __init__(self, parent):
        _Table.__init__(self, parent)
        self.doc = Documentation()
        self.suite_setup = Fixture()
        self.suite_teardown = Fixture()
        self.test_setup = Fixture()
        self.test_teardown = Fixture()
        self.test_timeout = Timeout()
        self.force_tags = Tags()
        self.default_tags = Tags()
        self.metadata = []
        self.imports = []

    def add_metadata(self, name, value, comment=None):
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


class VariableTable(_Table):

    def __init__(self, parent):
        _Table.__init__(self, parent)
        self.variables = []

    def add(self, name, value, comment=None):
        self.variables.append(Variable(name, value, comment))

    def __iter__(self):
        return iter(self.variables)


class TestCaseTable(_Table):

    def __init__(self, parent):
        _Table.__init__(self, parent)
        self.tests = []

    def add(self, name):
        self.tests.append(TestCase(self, name))
        return self.tests[-1]

    def __iter__(self):
        return iter(self.tests)


class KeywordTable(_Table):

    def __init__(self, parent):
        _Table.__init__(self, parent)
        self.keywords = []

    def add(self, name):
        self.keywords.append(UserKeyword(name))
        return self.keywords[-1]

    def __iter__(self):
        return iter(self.keywords)


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


class TestCase(_WithSteps):

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.doc = Documentation()
        self.tags = Tags()
        self.setup = Fixture()
        self.teardown = Fixture()
        self.timeout = Timeout()
        self.steps = []

    def add_for_loop(self, data):
        self.steps.append(ForLoop(data))
        return self.steps[-1]


class UserKeyword(TestCase):

    def __init__(self, name):
        self.name = name
        self.doc = Documentation()
        self.args = Arguments()
        self.return_ = Return()
        self.timeout = Timeout()
        self.steps = []


class ForLoop(_WithSteps):

    def __init__(self, content):
        self.range, index = self._get_range_and_index(content)
        self.vars = content[:index]
        self.values = content[index+1:]
        self.steps = []
        self.name = '%s %s [ %s ]' % (' | '.join(self.vars),
                                      self.range and 'IN RANGE' or 'IN',
                                      ' | '.join(self.values))

    def _get_range_and_index(self, content):
        for index, item in enumerate(content):
            if item.upper() in ['IN', 'IN RANGE']:
                return item.upper() == 'IN RANGE', index
        return False, len(content)


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
