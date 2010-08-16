#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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
                      Library, Resource, Variables, Arguments, Return, Template)
from populators import FromFilePopulator, FromDirectoryPopulator


def TestData(parent=None, source=None, include_suites=[]):
    if os.path.isdir(source):
        return TestDataDirectory(parent, source, include_suites)
    return TestCaseFile(parent, source)


class _TestData(object):

    def __init__(self, parent=None, source=None):
        self.parent = parent
        self.source = os.path.abspath(source) if source else None
        self.children = []
        self._tables = None

    def _get_tables(self):
        if not self._tables:
            self._tables = utils.NormalizedDict({'Setting': self.setting_table,
                                                 'Settings': self.setting_table,
                                                 'Metadata': self.setting_table,
                                                 'Variable': self.variable_table,
                                                 'Variables': self.variable_table,
                                                 'Keyword': self.keyword_table,
                                                 'Keywords': self.keyword_table,
                                                 'User Keyword': self.keyword_table,
                                                 'User Keywords': self.keyword_table,
                                                 'Test Case': self.testcase_table,
                                                 'Test Cases': self.testcase_table})
        return self._tables

    def start_table(self, header_row):
        table_name = header_row[0]
        try:
            table = self._valid_table(self._get_tables()[table_name])
        except KeyError:
            return None
        else:
            if table is not None:
                table.set_header(header_row)
            return table

    @property
    def name(self):
        if not self.source:
            return None
        name = os.path.splitext(os.path.basename(self.source))[0]
        name = name.split('__', 1)[-1]  # Strip possible prefix
        name = name.replace('_', ' ').strip()
        if name.islower():
            name = ' '.join(w[0].upper() + w[1:] for w in name.split())
        return name

    @property
    def keywords(self):
        return self.keyword_table.keywords

    @property
    def imports(self):
        return self.setting_table.imports

    def report_invalid_syntax(self, table, message, level='ERROR'):
        initfile = getattr(self, 'initfile', None)
        path = os.path.join(self.source, initfile) if initfile else self.source
        LOGGER.write("Invalid syntax in file '%s' in table '%s': %s"
                     % (path, table, message), level)


class TestCaseFile(_TestData):

    def __init__(self, parent=None, source=None):
        _TestData.__init__(self, parent, source)
        self.directory = os.path.dirname(self.source) if self.source else None
        self.setting_table = TestCaseFileSettingTable(self)
        self.variable_table = VariableTable(self)
        self.testcase_table = TestCaseTable(self)
        self.keyword_table = KeywordTable(self)
        if source: # FIXME: model should be decoupled from populating
            FromFilePopulator(self).populate(source)
            self._validate()

    def _validate(self):
        if not self.testcase_table.is_started():
            raise DataError('File has no test case table.')

    def _valid_table(self, table):
        return table

    def has_tests(self):
        return True

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
        self.testcase_table = TestCaseTable(self)
        self.keyword_table = KeywordTable(self)
        if self.source:
            FromFilePopulator(self).populate(source)
            self._report_status()

    def _report_status(self):
        if self.setting_table or self.variable_table or self.keyword_table:
            LOGGER.info("Imported resource file '%s' (%d keywords)."
                        % (self.source, len(self.keyword_table.keywords)))
        else:
            LOGGER.warn("Imported resource file '%s' is empty." % self.source)

    def _valid_table(self, table):
        if table is self.testcase_table:
            raise DataError('Test case table not allowed in resource file.')
        return table

    def __iter__(self):
        for table in [self.setting_table, self.variable_table,
                      self.keyword_table]:
            yield table


class TestDataDirectory(_TestData):

    def __init__(self, parent=None, source=None, include_suites=[]):
        _TestData.__init__(self, parent, source)
        self.directory = self.source
        self.initfile = None
        self.setting_table = InitFileSettingTable(self)
        self.variable_table = VariableTable(self)
        self.testcase_table = TestCaseTable(self)
        self.keyword_table = KeywordTable(self)
        if self.source:
            FromDirectoryPopulator().populate(self.source, self, include_suites)
            self.children = [ ch for ch in self.children if ch.has_tests() ]

    def _valid_table(self, table):
        if table is self.testcase_table:
            LOGGER.error('Test case table not allowed in test suite init file.')
            return None
        return table

    def add_child(self, path, include_suites):
        self.children.append(TestData(parent=self,source=path,
                                      include_suites=include_suites))

    def has_tests(self):
        return any(ch.has_tests() for ch in self.children)

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
        self.report_invalid_syntax("Non-existing setting '%s'." % setting_name)

    def is_setting(self, setting_name):
        return setting_name in self._setters


class _SettingTable(_Table, _WithSettings):
    type = 'setting'

    def __init__(self, parent):
        _Table.__init__(self, parent)
        self.doc = Documentation('Documentation', self)
        self.suite_setup = Fixture('Suite Setup', self)
        self.suite_teardown = Fixture('Suite Teardown', self)
        self.test_setup = Fixture('Test Setup', self)
        self.test_teardown = Fixture('Test Teardown', self)
        self.force_tags = Tags('Force Tags', self)
        self.default_tags = Tags('Default Tags', self)
        self.test_template = Template('Test Template', self)
        self.test_timeout = Timeout('Test Timeout', self)
        self.metadata = []
        self.imports = []
        self._setters = self._get_setters()

    def _get_adder(self, adder_method):
        def adder(value, comment):
            name = value[0] if value else ''
            adder_method(name, value[1:], comment)
        return adder

    def add_metadata(self, name, value='', comment=None):
        self.metadata.append(Metadata('Metadata', self, name, value, comment))
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

    def __nonzero__(self):
        return any(setting.is_set() for setting in self)


class TestCaseFileSettingTable(_SettingTable):

    def _get_setters(self):
        return utils.NormalizedDict({'Documentation': self.doc.populate,
                                     'Document': self.doc.populate,
                                     'Suite Setup': self.suite_setup.populate,
                                     'Suite Precondition': self.suite_setup.populate,
                                     'Suite Teardown': self.suite_teardown.populate,
                                     'Suite Postcondition': self.suite_teardown.populate,
                                     'Test Setup': self.test_setup.populate,
                                     'Test Precondition': self.test_setup.populate,
                                     'Test Teardown': self.test_teardown.populate,
                                     'Test Postcondition': self.test_teardown.populate,
                                     'Force Tags': self.force_tags.populate,
                                     'Default Tags': self.default_tags.populate,
                                     'Test Template': self.test_template.populate,
                                     'Test Timeout': self.test_timeout.populate,
                                     'Library': self._get_adder(self.add_library),
                                     'Resource': self._get_adder(self.add_resource),
                                     'Variables': self._get_adder(self.add_variables),
                                     'Metadata': self._get_adder(self.add_metadata)})

    def __iter__(self):
        for setting in [self.doc, self.suite_setup, self.suite_teardown,
                        self.test_setup, self.test_teardown, self.force_tags,
                        self.default_tags, self.test_template, self.test_timeout] \
                        + self.metadata + self.imports:
            yield setting


class ResourceFileSettingTable(_SettingTable):

    def _get_setters(self):
        return utils.NormalizedDict({'Documentation': self.doc.populate,
                                     'Document': self.doc.populate,
                                     'Library': self._get_adder(self.add_library),
                                     'Resource': self._get_adder(self.add_resource),
                                     'Variables': self._get_adder(self.add_variables)})

    def __iter__(self):
        for setting in [self.doc] + self.imports:
            yield setting


class InitFileSettingTable(_SettingTable):

    def _get_setters(self):
        return utils.NormalizedDict({'Documentation': self.doc.populate,
                                     'Document': self.doc.populate,
                                     'Suite Setup': self.suite_setup.populate,
                                     'Suite Precondition': self.suite_setup.populate,
                                     'Suite Teardown': self.suite_teardown.populate,
                                     'Suite Postcondition': self.suite_teardown.populate,
                                     'Test Setup': self.test_setup.populate,
                                     'Test Precondition': self.test_setup.populate,
                                     'Test Teardown': self.test_teardown.populate,
                                     'Test Postcondition': self.test_teardown.populate,
                                     'Force Tags': self.force_tags.populate,
                                     'Library': self._get_adder(self.add_library),
                                     'Resource': self._get_adder(self.add_resource),
                                     'Variables': self._get_adder(self.add_variables),
                                     'Metadata': self._get_adder(self.add_metadata)})

    def __iter__(self):
        for setting in [self.doc, self.suite_setup, self.suite_teardown,
                        self.test_setup, self.test_teardown, self.force_tags] \
                        + self.metadata + self.imports:
            yield setting


class VariableTable(_Table):
    type = 'variable'

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
    type = 'testcase'

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
    type = 'keyword'

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


class Variable(object):

    def __init__(self, name, value, comment=None):
        self.name = name.rstrip('= ')
        if name.startswith('$') and value == []:
            value = ''
        if isinstance(value, basestring):
            value = [value]  # Need to support scalar lists until RF 2.6
        self.value = value
        self.comment = comment

    def as_list(self):
        ret = [self.name] + self.value
        if self.comment:
            ret.append('# %s' % self.comment)
        return ret

    def is_set(self):
        return True

    def is_for_loop(self):
        return False


class _WithSteps(object):

    def add_step(self, content, comment=None):
        self.steps.append(Step(content, comment))
        return self.steps[-1]


class TestCase(_WithSteps, _WithSettings):

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.doc = Documentation('[Documentation]', self)
        self.template = Template('[Template]', self)
        self.tags = Tags('[Tags]', self)
        self.setup = Fixture('[Setup]', self)
        self.teardown = Fixture('[Teardown]', self)
        self.timeout = Timeout('[Timeout]', self)
        self.steps = []
        self._setters = self._get_setters()

    def _get_setters(self):
        return utils.NormalizedDict({'Documentation': self.doc.populate,
                                     'Document': self.doc.populate,
                                     'Template': self.template.populate,
                                     'Setup': self.setup.populate,
                                     'Precondition': self.setup.populate,
                                     'Teardown': self.teardown.populate,
                                     'Postcondition': self.teardown.populate,
                                     'Tags': self.tags.populate,
                                     'Timeout': self.timeout.populate})

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
        type_ = 'test case' if type(self) is TestCase else 'keyword'
        message = "Invalid syntax in %s '%s': %s" % (type_, self.name, message)
        self.parent.report_invalid_syntax(message, level)

    def __iter__(self):
        for element in [self.doc, self.tags, self.setup, 
                        self.template, self.timeout] \
                        + self.steps + [self.teardown]:
            yield element


class UserKeyword(TestCase):

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.doc = Documentation('[Documentation]', self)
        self.args = Arguments('[Arguments]', self)
        self.return_ = Return('[Return]', self)
        self.timeout = Timeout('[Timeout]', self)
        self.steps = []
        self._setters = self._get_setters()

    def _get_setters(self):
        return utils.NormalizedDict({'Documentation': self.doc.populate,
                                     'Document': self.doc.populate,
                                     'Arguments': self.args.populate,
                                     'Return': self.return_.populate,
                                     'Timeout': self.timeout.populate})

    def __iter__(self):
        for element in [self.args, self.doc, self.timeout] \
                        + self.steps + [self.return_]:
            yield element


class ForLoop(_WithSteps):

    def __init__(self, content):
        self.range, index = self._get_range_and_index(content)
        self.vars = content[:index]
        self.items = content[index+1:]
        self.steps = []

    def _get_range_and_index(self, content):
        for index, item in enumerate(content):
            item = item.upper().replace(' ', '')
            if item in ['IN', 'INRANGE']:
                return item == 'INRANGE', index
        return False, len(content)

    def is_comment(self):
        return False

    def is_for_loop(self):
        return True

    def apply_template(self, template):
        return self

    def as_list(self):
        return [': FOR'] + self.vars + ['IN RANGE' if self.range else 'IN'] + self.items

    def __iter__(self):
        return iter(self.steps)


class Step(object):

    def __init__(self, content, comment=None):
        self.assign = self._get_assigned_vars(content)
        try:
            self.keyword = content[len(self.assign)]
        except IndexError:
            self.keyword = None
        self.args = content[len(self.assign)+1:]
        self.comment = comment

    def _get_assigned_vars(self, content):
        vars = []
        for item in content:
            if not is_var(item.rstrip('= ')):
                break
            vars.append(item)
        return vars

    def is_comment(self):
        return not (self.assign or self.keyword or self.args)

    def is_for_loop(self):
        return False

    def apply_template(self, template):
        if self.is_comment():
            return self
        return Step([template] + self.as_list(include_comment=False))

    def is_set(self):
        return True

    def as_list(self, indent=False, include_comment=True):
        kw = [self.keyword] if self.keyword is not None else []
        ret = self.assign + kw + self.args
        if indent:
            ret.insert(0, '')
        if include_comment and self.comment:
            ret.append('# %s' % self.comment)
        return ret
