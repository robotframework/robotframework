#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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
import copy

from robot.errors import DataError
from robot.variables import is_var
from robot.output import LOGGER
from robot import utils
from robot.writer.serializer import Serializer, SerializationContext

from settings import (Documentation, Fixture, Timeout, Tags, Metadata,
    Library, Resource, Variables, Arguments, Return, Template, Comment)
from populators import FromFilePopulator, FromDirectoryPopulator


def TestData(parent=None, source=None, include_suites=[], warn_on_skipped=False):
    if os.path.isdir(source):
        return TestDataDirectory(parent, source).populate(include_suites, warn_on_skipped)
    return TestCaseFile(parent, source).populate()


class _TestData(object):
    _setting_table_names = 'Setting', 'Settings', 'Metadata'
    _variable_table_names = 'Variable', 'Variables'
    _testcase_table_names = 'Test Case', 'Test Cases'
    _keyword_table_names = 'Keyword', 'Keywords', 'User Keyword', 'User Keywords'

    def __init__(self, parent=None, source=None):
        self.parent = parent
        self.source = utils.abspath(source) if source else None
        self.children = []
        self._tables = utils.NormalizedDict(self._get_tables())

    def _get_tables(self):
        for names, table in [(self._setting_table_names, self.setting_table),
                             (self._variable_table_names, self.variable_table),
                             (self._testcase_table_names, self.testcase_table),
                             (self._keyword_table_names, self.keyword_table)]:
            for name in names:
                yield name, table

    def start_table(self, header_row):
        try:
            table = self._tables[header_row[0]]
        except (KeyError, IndexError):
            return None
        if not self._table_is_allowed(table):
            return None
        table.set_header(header_row)
        return table

    @property
    def name(self):
        return self._format_name(self._get_basename()) if self.source else None

    def _get_basename(self):
        return os.path.splitext(os.path.basename(self.source))[0]

    def _format_name(self, name):
        name = self._strip_possible_prefix_from_name(name)
        name = name.replace('_', ' ').strip()
        return name.title() if name.islower() else name

    def _strip_possible_prefix_from_name(self, name):
        return name.split('__', 1)[-1]

    @property
    def keywords(self):
        return self.keyword_table.keywords

    @property
    def imports(self):
        return self.setting_table.imports

    def report_invalid_syntax(self, table, message, level='ERROR'):
        initfile = getattr(self, 'initfile', None)
        path = os.path.join(self.source, initfile) if initfile else self.source
        LOGGER.write("Error in file '%s' in table '%s': %s"
                     % (path, table, message), level)

    def save(self, **options):
        """Serializes this datafile.

        :param **options: Configuration for serialization. Any optional arguments
            of robot.writer.serializer.SerializationContext can be given.
        """
        Serializer().serialize(self, **options)


class TestCaseFile(_TestData):

    def __init__(self, parent=None, source=None):
        self.directory = os.path.dirname(source) if source else None
        self.setting_table = TestCaseFileSettingTable(self)
        self.variable_table = VariableTable(self)
        self.testcase_table = TestCaseTable(self)
        self.keyword_table = KeywordTable(self)
        _TestData.__init__(self, parent, source)

    def populate(self):
        FromFilePopulator(self).populate(self.source)
        self._validate()
        return self

    def _validate(self):
        if not self.testcase_table.is_started():
            raise DataError('File has no test case table.')

    def _table_is_allowed(self, table):
        return True

    def has_tests(self):
        return True

    def __iter__(self):
        for table in [self.setting_table, self.variable_table,
                      self.testcase_table, self.keyword_table]:
            yield table


class ResourceFile(_TestData):

    def __init__(self, source=None):
        self.directory = os.path.dirname(source) if source else None
        self.setting_table = ResourceFileSettingTable(self)
        self.variable_table = VariableTable(self)
        self.testcase_table = TestCaseTable(self)
        self.keyword_table = KeywordTable(self)
        _TestData.__init__(self, source=source)

    def populate(self):
        FromFilePopulator(self).populate(self.source)
        self._report_status()
        return self

    def _report_status(self):
        if self.setting_table or self.variable_table or self.keyword_table:
            LOGGER.info("Imported resource file '%s' (%d keywords)."
                        % (self.source, len(self.keyword_table.keywords)))
        else:
            LOGGER.warn("Imported resource file '%s' is empty." % self.source)

    def _table_is_allowed(self, table):
        if table is self.testcase_table:
            raise DataError("Resource file '%s' contains a test case table "
                            "which is not allowed." % self.source)
        return True

    def __iter__(self):
        for table in [self.setting_table, self.variable_table, self.keyword_table]:
            yield table


class TestDataDirectory(_TestData):

    def __init__(self, parent=None, source=None):
        self.directory = source
        self.initfile = None
        self.setting_table = InitFileSettingTable(self)
        self.variable_table = VariableTable(self)
        self.testcase_table = TestCaseTable(self)
        self.keyword_table = KeywordTable(self)
        _TestData.__init__(self, parent, source)

    def populate(self, include_suites=[], warn_on_skipped=False):
        FromDirectoryPopulator().populate(self.source, self, include_suites,
                                          warn_on_skipped)
        self.children = [ch for ch in self.children if ch.has_tests()]
        return self

    def _get_basename(self):
        return os.path.basename(self.source)

    def _table_is_allowed(self, table):
        if table is self.testcase_table:
            LOGGER.error("Test suite init file in '%s' contains a test case "
                         "table which is not allowed." % self.source)
            return False
        return True

    def add_child(self, path, include_suites):
        self.children.append(TestData(parent=self,source=path,
                                      include_suites=include_suites))

    def has_tests(self):
        return any(ch.has_tests() for ch in self.children)

    def __iter__(self):
        for table in [self.setting_table, self.variable_table, self.keyword_table]:
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
        normalized = self.normalize(setting_name)
        if normalized in self._setters:
            return self._setters[normalized](self)
        self.report_invalid_syntax("Non-existing setting '%s'." % setting_name)

    def is_setting(self, setting_name):
        return self.normalize(setting_name) in self._setters

    def normalize(self, setting):
        result = utils.normalize(setting)
        return result[0:-1] if result and result[-1]==':' else result


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

    _setters = {'documentation': lambda s: s.doc.populate,
                'document': lambda s: s.doc.populate,
                'suitesetup': lambda s: s.suite_setup.populate,
                'suiteprecondition': lambda s: s.suite_setup.populate,
                'suiteteardown': lambda s: s.suite_teardown.populate,
                'suitepostcondition': lambda s: s.suite_teardown.populate,
                'testsetup': lambda s: s.test_setup.populate,
                'testprecondition': lambda s: s.test_setup.populate,
                'testteardown': lambda s: s.test_teardown.populate,
                'testpostcondition': lambda s: s.test_teardown.populate,
                'forcetags': lambda s: s.force_tags.populate,
                'defaulttags': lambda s: s.default_tags.populate,
                'testtemplate': lambda s: s.test_template.populate,
                'testtimeout': lambda s: s.test_timeout.populate,
                'library': lambda s: s._get_adder(s.add_library),
                'resource': lambda s: s._get_adder(s.add_resource),
                'variables': lambda s: s._get_adder(s.add_variables),
                'metadata': lambda s: s._get_adder(s.add_metadata)}

    def __iter__(self):
        for setting in [self.doc, self.suite_setup, self.suite_teardown,
                        self.test_setup, self.test_teardown, self.force_tags,
                        self.default_tags, self.test_template, self.test_timeout] \
                        + self.metadata + self.imports:
            yield setting


class ResourceFileSettingTable(_SettingTable):

    _setters = {'documentation': lambda s: s.doc.populate,
                'document': lambda s: s.doc.populate,
                'library': lambda s: s._get_adder(s.add_library),
                'resource': lambda s: s._get_adder(s.add_resource),
                'variables': lambda s: s._get_adder(s.add_variables)}

    def __iter__(self):
        for setting in [self.doc] + self.imports:
            yield setting


class InitFileSettingTable(_SettingTable):

    _setters = {'documentation': lambda s: s.doc.populate,
                'document': lambda s: s.doc.populate,
                'suitesetup': lambda s: s.suite_setup.populate,
                'suiteprecondition': lambda s: s.suite_setup.populate,
                'suiteteardown': lambda s: s.suite_teardown.populate,
                'suitepostcondition': lambda s: s.suite_teardown.populate,
                'testsetup': lambda s: s.test_setup.populate,
                'testprecondition': lambda s: s.test_setup.populate,
                'testteardown': lambda s: s.test_teardown.populate,
                'testpostcondition': lambda s: s.test_teardown.populate,
                'forcetags': lambda s: s.force_tags.populate,
                'library': lambda s: s._get_adder(s.add_library),
                'resource': lambda s: s._get_adder(s.add_resource),
                'variables': lambda s: s._get_adder(s.add_variables),
                'metadata': lambda s: s._get_adder(s.add_metadata)}

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
            value = [value]  # Must support scalar lists until RF 2.7 (issue 939)
        self.value = value
        self.comment = Comment(comment)

    def as_list(self):
        return [self.name] + self.value + self.comment.as_list()

    def is_set(self):
        return True

    def is_for_loop(self):
        return False


class _WithSteps(object):

    def add_step(self, content, comment=None):
        self.steps.append(Step(content, comment))
        return self.steps[-1]

    def copy(self, name):
        new = copy.deepcopy(self)
        new.name = name
        self._add_to_parent(new)
        return new


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

    _setters = {'documentation': lambda s: s.doc.populate,
                'document': lambda s: s.doc.populate,
                'template': lambda s: s.template.populate,
                'setup': lambda s: s.setup.populate,
                'precondition': lambda s: s.setup.populate,
                'teardown': lambda s: s.teardown.populate,
                'postcondition': lambda s: s.teardown.populate,
                'tags': lambda s: s.tags.populate,
                'timeout': lambda s: s.timeout.populate}

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

    def _add_to_parent(self, test):
        self.parent.tests.append(test)

    @property
    def settings(self):
        return [self.doc, self.tags, self.setup, self.template, self.timeout,
                self.teardown]

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
        self.teardown = Fixture('[Teardown]', self)
        self.steps = []

    _setters = {'documentation': lambda s: s.doc.populate,
                'document': lambda s: s.doc.populate,
                'arguments': lambda s: s.args.populate,
                'return': lambda s: s.return_.populate,
                'timeout': lambda s: s.timeout.populate,
                'teardown': lambda s: s.teardown.populate}

    def _add_to_parent(self, test):
        self.parent.keywords.append(test)

    @property
    def settings(self):
        return [self.args, self.doc, self.timeout, self.teardown, self.return_]

    def __iter__(self):
        for element in [self.args, self.doc, self.timeout] \
                        + self.steps + [self.teardown, self.return_]:
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

    def as_list(self, indent=False, include_comment=False):
        return [': FOR'] + self.vars + ['IN RANGE' if self.range else 'IN'] + self.items

    def __iter__(self):
        return iter(self.steps)


class Step(object):

    def __init__(self, content, comment=None):
        self.assign = list(self._get_assigned_vars(content))
        try:
            self.keyword = content[len(self.assign)]
        except IndexError:
            self.keyword = None
        self.args = content[len(self.assign)+1:]
        self.comment = Comment(comment)

    def _get_assigned_vars(self, content):
        for item in content:
            if not is_var(item.rstrip('= ')):
                return
            yield item

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
            ret += self.comment.as_list()
        return ret
