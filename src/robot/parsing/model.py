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

import os
import copy

from robot.errors import DataError
from robot.variables import is_var
from robot.output import LOGGER
from robot.writer import DataFileWriter
from robot.utils import abspath, is_string, normalize, py2to3, NormalizedDict

from .comments import Comment
from .populators import FromFilePopulator, FromDirectoryPopulator
from .settings import (Documentation, Fixture, Timeout, Tags, Metadata,
                       Library, Resource, Variables, Arguments, Return,
                       Template, MetadataList, ImportList)


def TestData(parent=None, source=None, include_suites=None,
             warn_on_skipped=False, extensions=None):
    """Parses a file or directory to a corresponding model object.

    :param parent: Optional parent to be used in creation of the model object.
    :param source: Path where test data is read from.
    :param warn_on_skipped: Boolean to control warning about skipped files.
    :param extensions: List/set of extensions to parse. If None, all files
        supported by Robot Framework are parsed when searching test cases.
    :returns: :class:`~.model.TestDataDirectory`  if `source` is a directory,
        :class:`~.model.TestCaseFile` otherwise.
    """
    if os.path.isdir(source):
        return TestDataDirectory(parent, source).populate(include_suites,
                                                          warn_on_skipped,
                                                          extensions)
    return TestCaseFile(parent, source).populate()


class _TestData(object):
    _setting_table_names = 'Setting', 'Settings', 'Metadata'
    _variable_table_names = 'Variable', 'Variables'
    _testcase_table_names = 'Test Case', 'Test Cases'
    _keyword_table_names = 'Keyword', 'Keywords', 'User Keyword', 'User Keywords'
    _deprecated = NormalizedDict({'Metadata': 'Settings',
                                  'User Keyword': 'Keywords',
                                  'User Keywords': 'Keywords'})

    def __init__(self, parent=None, source=None):
        self.parent = parent
        self.source = abspath(source) if source else None
        self.children = []
        self._tables = NormalizedDict(self._get_tables())

    def _get_tables(self):
        for names, table in [(self._setting_table_names, self.setting_table),
                             (self._variable_table_names, self.variable_table),
                             (self._testcase_table_names, self.testcase_table),
                             (self._keyword_table_names, self.keyword_table)]:
            for name in names:
                yield name, table

    def start_table(self, header_row):
        try:
            name = header_row[0]
            table = self._tables[name]
            if name in self._deprecated:
                self._report_deprecated(name)
        except (KeyError, IndexError):
            return None
        if not self._table_is_allowed(table):
            return None
        table.set_header(header_row)
        return table

    # TODO: Remove support for deprecated tables altogether in RF 3.1.
    def _report_deprecated(self, name):
        self.report_invalid_syntax(
            "Table name '%s' is deprecated. Please use '%s' instead."
            % (name, self._deprecated[name]), level='WARN')

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

    def report_invalid_syntax(self, message, level='ERROR'):
        initfile = getattr(self, 'initfile', None)
        path = os.path.join(self.source, initfile) if initfile else self.source
        LOGGER.write("Error in file '%s': %s" % (path, message), level)

    def save(self, **options):
        """Writes this datafile to disk.

        :param options: Configuration for writing. These are passed to
            :py:class:`~robot.writer.datafilewriter.WritingContext` as
            keyword arguments.

        See also :py:class:`robot.writer.datafilewriter.DataFileWriter`
        """
        return DataFileWriter(**options).write(self)


class TestCaseFile(_TestData):
    """The parsed test case file object.

    :param parent: parent object to be used in creation of the model object.
    :param source: path where test data is read from.
    """

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
    """The parsed resource file object.

    :param source: path where resource file is read from.
    """

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
    """The parsed test data directory object. Contains hiearchical structure
    of other :py:class:`.TestDataDirectory` and :py:class:`.TestCaseFile`
    objects.

    :param parent: parent object to be used in creation of the model object.
    :param source: path where test data is read from.
    """

    def __init__(self, parent=None, source=None):
        self.directory = source
        self.initfile = None
        self.setting_table = InitFileSettingTable(self)
        self.variable_table = VariableTable(self)
        self.testcase_table = TestCaseTable(self)
        self.keyword_table = KeywordTable(self)
        _TestData.__init__(self, parent, source)

    def populate(self, include_suites=None, warn_on_skipped=False,
                 extensions=None, recurse=True):
        FromDirectoryPopulator().populate(self.source, self, include_suites,
                                          warn_on_skipped, extensions, recurse)
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

    def add_child(self, path, include_suites, extensions=None,
                  warn_on_skipped=False):
        self.children.append(TestData(parent=self,
                                      source=path,
                                      include_suites=include_suites,
                                      extensions=extensions,
                                      warn_on_skipped=warn_on_skipped))

    def has_tests(self):
        return any(ch.has_tests() for ch in self.children)

    def __iter__(self):
        for table in [self.setting_table, self.variable_table, self.keyword_table]:
            yield table


@py2to3
class _Table(object):

    def __init__(self, parent):
        self.parent = parent
        self._header = None

    def set_header(self, header):
        self._header = self._prune_old_style_headers(header)

    def _prune_old_style_headers(self, header):
        if len(header) < 3:
            return header
        if self._old_header_matcher.match(header):
            return [header[0]]
        return header

    @property
    def header(self):
        return self._header or [self.type.title() + 's']

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
        self.parent.report_invalid_syntax(message, level)

    def __nonzero__(self):
        return bool(self._header or len(self))

    def __len__(self):
        return sum(1 for item in self)


class _WithSettings(object):
    _deprecated = {'document': 'Documentation',
                   'suiteprecondition': 'Suite Setup',
                   'suitepostcondition': 'Suite Teardown',
                   'testprecondition': 'Test Setup',
                   'testpostcondition': 'Test Teardown',
                   'precondition': 'Setup',
                   'postcondition': 'Teardown'}

    def get_setter(self, setting_name):
        normalized = self.normalize(setting_name)
        if normalized in self._deprecated:
            self._report_deprecated(setting_name, self._deprecated[normalized])
            normalized = self.normalize(self._deprecated[normalized])
        if normalized in self._setters:
            return self._setters[normalized](self)
        self.report_invalid_syntax("Non-existing setting '%s'." % setting_name)

    def _report_deprecated(self, deprecated, use_instead):
         self.report_invalid_syntax(
             "Setting '%s' is deprecated. Use '%s' instead."
             % (deprecated.rstrip(':'), use_instead), level='WARN')

    def is_setting(self, setting_name):
        return self.normalize(setting_name) in self._setters

    def normalize(self, setting):
        result = normalize(setting)
        return result[:-1] if result[-1:] == ':' else result


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
        self.metadata = MetadataList(self)
        self.imports = ImportList(self)

    @property
    def _old_header_matcher(self):
        return OldStyleSettingAndVariableTableHeaderMatcher()

    def add_metadata(self, name, value='', comment=None):
        self.metadata.add(Metadata(self, name, value, comment))
        return self.metadata[-1]

    def add_library(self, name, args=None, comment=None):
        self.imports.add(Library(self, name, args, comment=comment))
        return self.imports[-1]

    def add_resource(self, name, invalid_args=None, comment=None):
        self.imports.add(Resource(self, name, invalid_args, comment=comment))
        return self.imports[-1]

    def add_variables(self, name, args=None, comment=None):
        self.imports.add(Variables(self, name, args, comment=comment))
        return self.imports[-1]

    def __len__(self):
        return sum(1 for setting in self if setting.is_set())


class TestCaseFileSettingTable(_SettingTable):

    _setters = {'documentation': lambda s: s.doc.populate,
                'suitesetup': lambda s: s.suite_setup.populate,
                'suiteteardown': lambda s: s.suite_teardown.populate,
                'testsetup': lambda s: s.test_setup.populate,
                'testteardown': lambda s: s.test_teardown.populate,
                'forcetags': lambda s: s.force_tags.populate,
                'defaulttags': lambda s: s.default_tags.populate,
                'testtemplate': lambda s: s.test_template.populate,
                'testtimeout': lambda s: s.test_timeout.populate,
                'library': lambda s: s.imports.populate_library,
                'resource': lambda s: s.imports.populate_resource,
                'variables': lambda s: s.imports.populate_variables,
                'metadata': lambda s: s.metadata.populate}

    def __iter__(self):
        for setting in [self.doc, self.suite_setup, self.suite_teardown,
                        self.test_setup, self.test_teardown, self.force_tags,
                        self.default_tags, self.test_template, self.test_timeout] \
                        + self.metadata.data + self.imports.data:
            yield setting


class ResourceFileSettingTable(_SettingTable):

    _setters = {'documentation': lambda s: s.doc.populate,
                'library': lambda s: s.imports.populate_library,
                'resource': lambda s: s.imports.populate_resource,
                'variables': lambda s: s.imports.populate_variables}

    def __iter__(self):
        for setting in [self.doc] + self.imports.data:
            yield setting


class InitFileSettingTable(_SettingTable):

    _setters = {'documentation': lambda s: s.doc.populate,
                'suitesetup': lambda s: s.suite_setup.populate,
                'suiteteardown': lambda s: s.suite_teardown.populate,
                'testsetup': lambda s: s.test_setup.populate,
                'testteardown': lambda s: s.test_teardown.populate,
                'testtimeout': lambda s: s.test_timeout.populate,
                'forcetags': lambda s: s.force_tags.populate,
                'library': lambda s: s.imports.populate_library,
                'resource': lambda s: s.imports.populate_resource,
                'variables': lambda s: s.imports.populate_variables,
                'metadata': lambda s: s.metadata.populate}

    def __iter__(self):
        for setting in [self.doc, self.suite_setup, self.suite_teardown,
                        self.test_setup, self.test_teardown, self.force_tags,
                        self.test_timeout] + self.metadata.data + self.imports.data:
            yield setting


class VariableTable(_Table):
    type = 'variable'

    def __init__(self, parent):
        _Table.__init__(self, parent)
        self.variables = []

    @property
    def _old_header_matcher(self):
        return OldStyleSettingAndVariableTableHeaderMatcher()

    def add(self, name, value, comment=None):
        self.variables.append(Variable(self, name, value, comment))

    def __iter__(self):
        return iter(self.variables)


@py2to3
class TestCaseTable(_Table):
    type = 'test case'

    def __init__(self, parent):
        _Table.__init__(self, parent)
        self.tests = []

    @property
    def _old_header_matcher(self):
        return OldStyleTestAndKeywordTableHeaderMatcher()

    def add(self, name):
        self.tests.append(TestCase(self, name))
        return self.tests[-1]

    def __iter__(self):
        return iter(self.tests)

    def is_started(self):
        return bool(self._header)

    def __nonzero__(self):
        return True


class KeywordTable(_Table):
    type = 'keyword'

    def __init__(self, parent):
        _Table.__init__(self, parent)
        self.keywords = []

    @property
    def _old_header_matcher(self):
        return OldStyleTestAndKeywordTableHeaderMatcher()

    def add(self, name):
        self.keywords.append(UserKeyword(self, name))
        return self.keywords[-1]

    def __iter__(self):
        return iter(self.keywords)


@py2to3
class Variable(object):

    def __init__(self, parent, name, value, comment=None):
        self.parent = parent
        self.name = name.rstrip('= ')
        if name.startswith('$') and value == []:
            value = ''
        if is_string(value):
            value = [value]
        self.value = value
        self.comment = Comment(comment)

    def as_list(self):
        if self.has_data():
            return [self.name] + self.value + self.comment.as_list()
        return self.comment.as_list()

    def is_set(self):
        return True

    def is_for_loop(self):
        return False

    def has_data(self):
        return bool(self.name or ''.join(self.value))

    def __nonzero__(self):
        return self.has_data()

    def report_invalid_syntax(self, message, level='ERROR'):
        self.parent.report_invalid_syntax("Setting variable '%s' failed: %s"
                                          % (self.name, message), level)


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
                'template': lambda s: s.template.populate,
                'setup': lambda s: s.setup.populate,
                'teardown': lambda s: s.teardown.populate,
                'tags': lambda s: s.tags.populate,
                'timeout': lambda s: s.timeout.populate}

    @property
    def source(self):
        return self.parent.source

    @property
    def directory(self):
        return self.parent.directory

    def add_for_loop(self, declaration, comment=None):
        self.steps.append(ForLoop(declaration, comment))
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
        self.tags = Tags('[Tags]', self)
        self.steps = []

    _setters = {'documentation': lambda s: s.doc.populate,
                'arguments': lambda s: s.args.populate,
                'return': lambda s: s.return_.populate,
                'timeout': lambda s: s.timeout.populate,
                'teardown': lambda s: s.teardown.populate,
                'tags': lambda s: s.tags.populate}

    def _add_to_parent(self, test):
        self.parent.keywords.append(test)

    @property
    def settings(self):
        return [self.args, self.doc, self.tags, self.timeout, self.teardown, self.return_]

    def __iter__(self):
        for element in [self.args, self.doc, self.tags, self.timeout] \
                        + self.steps + [self.teardown, self.return_]:
            yield element


class ForLoop(_WithSteps):
    """The parsed representation of a for-loop.

    :param list declaration: The literal cell values that declare the loop
                             (excluding ":FOR").
    :param str comment: A comment, default None.
    :ivar str flavor: The value of the 'IN' item, uppercased.
                      Typically 'IN', 'IN RANGE', 'IN ZIP', or 'IN ENUMERATE'.
    :ivar list vars: Variables set per-iteration by this loop.
    :ivar list items: Loop values that come after the 'IN' item.
    :ivar str comment: A comment, or None.
    :ivar list steps: A list of steps in the loop.
    """

    def __init__(self, declaration, comment=None):
        self.flavor, index = self._get_flavors_and_index(declaration)
        self.vars = declaration[:index]
        self.items = declaration[index+1:]
        self.comment = Comment(comment)
        self.steps = []

    def _get_flavors_and_index(self, declaration):
        for index, item in enumerate(declaration):
            item = item.upper()
            if item.replace(' ', '').startswith('IN'):
                return item, index
        return 'IN', len(declaration)

    def is_comment(self):
        return False

    def is_for_loop(self):
        return True

    def as_list(self, indent=False, include_comment=True):
        comments = self.comment.as_list() if include_comment else []
        return  [': FOR'] + self.vars + [self.flavor] + self.items + comments

    def __iter__(self):
        return iter(self.steps)

    def is_set(self):
        return True


class Step(object):

    def __init__(self, content, comment=None):
        self.assign = self._get_assign(content)
        self.name = content.pop(0) if content else None
        self.args = content
        self.comment = Comment(comment)

    def _get_assign(self, content):
        assign = []
        while content and is_var(content[0].rstrip('= ')):
            assign.append(content.pop(0))
        return assign

    def is_comment(self):
        return not (self.assign or self.name or self.args)

    def is_for_loop(self):
        return False

    def is_set(self):
        return True

    def as_list(self, indent=False, include_comment=True):
        kw = [self.name] if self.name is not None else []
        comments = self.comment.as_list() if include_comment else []
        data = self.assign + kw + self.args + comments
        if indent:
            data.insert(0, '')
        return data


class OldStyleSettingAndVariableTableHeaderMatcher(object):

    def match(self, header):
        return all((True if e.lower() == 'value' else False)
                    for e in header[1:])


class OldStyleTestAndKeywordTableHeaderMatcher(object):

    def match(self, header):
        if header[1].lower() != 'action':
            return False
        for h in header[2:]:
            if not h.lower().startswith('arg'):
                return False
        return True
