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
import warnings

from robot.errors import DataError
from robot.variables import is_var
from robot.output import LOGGER
from robot.writer import DataFileWriter
from robot.utils import abspath, is_string, normalize, py2to3, NormalizedDict

from .comments import Comment
from .populators import FromFilePopulator, FromDirectoryPopulator, NoTestsFound
from .settings import (Documentation, Fixture, Timeout, Tags, Metadata,
                       Library, Resource, Variables, Arguments, Return,
                       Template, MetadataList, ImportList)


def TestData(parent=None, source=None, include_suites=None,
             warn_on_skipped='DEPRECATED', extensions=None):
    """Parses a file or directory to a corresponding model object.

    :param parent: Optional parent to be used in creation of the model object.
    :param source: Path where test data is read from.
    :param warn_on_skipped: Deprecated.
    :param extensions: List/set of extensions to parse. If None, all files
        supported by Robot Framework are parsed when searching test cases.
    :returns: :class:`~.model.TestDataDirectory`  if `source` is a directory,
        :class:`~.model.TestCaseFile` otherwise.
    """
    # TODO: Remove in RF 3.2.
    if warn_on_skipped != 'DEPRECATED':
        warnings.warn("Option 'warn_on_skipped' is deprecated and has no "
                      "effect.", DeprecationWarning)
    if os.path.isdir(source):
        return TestDataDirectory(parent, source).populate(include_suites,
                                                          extensions)
    return TestCaseFile(parent, source).populate()


class _TestData(object):
    _setting_table_names = 'Setting', 'Settings'
    _variable_table_names = 'Variable', 'Variables'
    _testcase_table_names = 'Test Case', 'Test Cases', 'Task', 'Tasks'
    _keyword_table_names = 'Keyword', 'Keywords'
    _comment_table_names = 'Comment', 'Comments'

    def __init__(self, parent=None, source=None):
        self.parent = parent
        self.source = abspath(source) if source else None
        self.children = []
        self._tables = dict(self._get_tables())

    def _get_tables(self):
        for names, table in [(self._setting_table_names, self.setting_table),
                             (self._variable_table_names, self.variable_table),
                             (self._testcase_table_names, self.testcase_table),
                             (self._keyword_table_names, self.keyword_table),
                             (self._comment_table_names, None)]:
            for name in names:
                yield name, table

    def start_table(self, header_row):
        table = self._find_table(header_row)
        if table is None or not self._table_is_allowed(table):
            return None
        table.set_header(header_row)
        return table

    def _find_table(self, header_row):
        name = header_row[0] if header_row else ''
        title = name.title()
        if title not in self._tables:
            title = self._resolve_deprecated_table(name)
            if title is None:
                self._report_unrecognized_table(name)
                return None
        return self._tables[title]

    def _resolve_deprecated_table(self, used_name):
        normalized = normalize(used_name)
        for name in (self._setting_table_names + self._variable_table_names +
                     self._testcase_table_names + self._keyword_table_names +
                     self._comment_table_names):
            if normalize(name) == normalized:
                self._report_deprecated_table(used_name, name)
                return name
        return None

    def _report_deprecated_table(self, deprecated, name):
        self.report_invalid_syntax(
            "Section name '%s' is deprecated. Use '%s' instead."
            % (deprecated, name), level='WARN'
        )

    def _report_unrecognized_table(self, name):
        self.report_invalid_syntax(
            "Unrecognized table header '%s'. Available headers for data: "
            "'Setting(s)', 'Variable(s)', 'Test Case(s)', 'Task(s)' and "
            "'Keyword(s)'. Use 'Comment(s)' to embedded additional data."
            % name
        )

    def _table_is_allowed(self, table):
        return True

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


@py2to3
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
            raise NoTestsFound('File has no tests or tasks.')

    def has_tests(self):
        return True

    def __iter__(self):
        for table in [self.setting_table, self.variable_table,
                      self.testcase_table, self.keyword_table]:
            yield table

    def __nonzero__(self):
        return any(table for table in self)


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
        FromFilePopulator(self).populate(self.source, resource=True)
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
            raise DataError("Resource file '%s' cannot contain tests or "
                            "tasks." % self.source)
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

    def populate(self, include_suites=None, extensions=None, recurse=True):
        FromDirectoryPopulator().populate(self.source, self, include_suites,
                                          extensions, recurse)
        self.children = [ch for ch in self.children if ch.has_tests()]
        return self

    def _get_basename(self):
        return os.path.basename(self.source)

    def _table_is_allowed(self, table):
        if table is self.testcase_table:
            LOGGER.error("Test suite initialization file in '%s' cannot "
                         "contain tests or tasks." % self.source)
            return False
        return True

    def add_child(self, path, include_suites, extensions=None):
        self.children.append(TestData(parent=self,
                                      source=path,
                                      include_suites=include_suites,
                                      extensions=extensions))

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
    _setters = {}
    _aliases = {}

    def get_setter(self, name):
        if name[-1:] == ':':
            name = name[:-1]
        setter = self._get_setter(name)
        if setter is not None:
            return setter
        setter = self._get_deprecated_setter(name)
        if setter is not None:
            return setter
        self.report_invalid_syntax("Non-existing setting '%s'." % name)
        return None

    def _get_setter(self, name):
        title = name.title()
        if title in self._aliases:
            title = self._aliases[name]
        if title in self._setters:
            return self._setters[title](self)
        return None

    def _get_deprecated_setter(self, name):
        normalized = normalize(name)
        for setting in list(self._setters) + list(self._aliases):
            if normalize(setting) == normalized:
                self._report_deprecated_setting(name, setting)
                return self._get_setter(setting)
        return None

    def _report_deprecated_setting(self, deprecated, correct):
        self.report_invalid_syntax(
            "Setting '%s' is deprecated. Use '%s' instead."
            % (deprecated, correct), level='WARN'
        )

    def report_invalid_syntax(self, message, level='ERROR'):
        raise NotImplementedError


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
    _setters = {'Documentation': lambda s: s.doc.populate,
                'Suite Setup': lambda s: s.suite_setup.populate,
                'Suite Teardown': lambda s: s.suite_teardown.populate,
                'Test Setup': lambda s: s.test_setup.populate,
                'Test Teardown': lambda s: s.test_teardown.populate,
                'Force Tags': lambda s: s.force_tags.populate,
                'Default Tags': lambda s: s.default_tags.populate,
                'Test Template': lambda s: s.test_template.populate,
                'Test Timeout': lambda s: s.test_timeout.populate,
                'Library': lambda s: s.imports.populate_library,
                'Resource': lambda s: s.imports.populate_resource,
                'Variables': lambda s: s.imports.populate_variables,
                'Metadata': lambda s: s.metadata.populate}
    _aliases = {'Task Setup': 'Test Setup',
                'Task Teardown': 'Test Teardown',
                'Task Template': 'Test Template',
                'Task Timeout': 'Test Timeout'}

    def __iter__(self):
        for setting in [self.doc, self.suite_setup, self.suite_teardown,
                        self.test_setup, self.test_teardown, self.force_tags,
                        self.default_tags, self.test_template, self.test_timeout] \
                        + self.metadata.data + self.imports.data:
            yield setting


class ResourceFileSettingTable(_SettingTable):
    _setters = {'Documentation': lambda s: s.doc.populate,
                'Library': lambda s: s.imports.populate_library,
                'Resource': lambda s: s.imports.populate_resource,
                'Variables': lambda s: s.imports.populate_variables}

    def __iter__(self):
        for setting in [self.doc] + self.imports.data:
            yield setting


class InitFileSettingTable(_SettingTable):
    _setters = {'Documentation': lambda s: s.doc.populate,
                'Suite Setup': lambda s: s.suite_setup.populate,
                'Suite Teardown': lambda s: s.suite_teardown.populate,
                'Test Setup': lambda s: s.test_setup.populate,
                'Test Teardown': lambda s: s.test_teardown.populate,
                'Test Timeout': lambda s: s.test_timeout.populate,
                'Force Tags': lambda s: s.force_tags.populate,
                'Library': lambda s: s.imports.populate_library,
                'Resource': lambda s: s.imports.populate_resource,
                'Variables': lambda s: s.imports.populate_variables,
                'Metadata': lambda s: s.metadata.populate}

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


class TestCaseTable(_Table):
    type = 'test case'

    def __init__(self, parent):
        _Table.__init__(self, parent)
        self.tests = []

    def set_header(self, header):
        if self._header and header:
            self._validate_mode(self._header[0], header[0])
        _Table.set_header(self, header)

    def _validate_mode(self, name1, name2):
        tasks1 = normalize(name1) in ('task', 'tasks')
        tasks2 = normalize(name2) in ('task', 'tasks')
        if tasks1 is not tasks2:
            raise DataError('One file cannot have both tests and tasks.')

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

    _setters = {'Documentation': lambda s: s.doc.populate,
                'Template': lambda s: s.template.populate,
                'Setup': lambda s: s.setup.populate,
                'Teardown': lambda s: s.teardown.populate,
                'Tags': lambda s: s.tags.populate,
                'Timeout': lambda s: s.timeout.populate}

    @property
    def source(self):
        return self.parent.source

    @property
    def directory(self):
        return self.parent.directory

    def add_for_loop(self, declaration, comment=None):
        self.steps.append(ForLoop(self, declaration, comment))
        return self.steps[-1]

    def end_for_loop(self):
        loop, steps = self._find_last_empty_for_and_steps_after()
        if not loop:
            return False
        loop.steps.extend(steps)
        self.steps[-len(steps):] = []
        return True

    def _find_last_empty_for_and_steps_after(self):
        steps = []
        for step in reversed(self.steps):
            if isinstance(step, ForLoop):
                if not step.steps:
                    steps.reverse()
                    return step, steps
                break
            steps.append(step)
        return None, []

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

    _setters = {'Documentation': lambda s: s.doc.populate,
                'Arguments': lambda s: s.args.populate,
                'Return': lambda s: s.return_.populate,
                'Timeout': lambda s: s.timeout.populate,
                'Teardown': lambda s: s.teardown.populate,
                'Tags': lambda s: s.tags.populate}

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
    flavors = {'IN', 'IN RANGE', 'IN ZIP', 'IN ENUMERATE'}
    normalized_flavors = NormalizedDict((f, f) for f in flavors)

    def __init__(self, parent, declaration, comment=None):
        self.parent = parent
        self.flavor, index = self._get_flavor_and_index(declaration)
        self.vars = declaration[:index]
        self.items = declaration[index+1:]
        self.comment = Comment(comment)
        self.steps = []

    def _get_flavor_and_index(self, declaration):
        for index, item in enumerate(declaration):
            if item in self.flavors:
                return item, index
            if item in self.normalized_flavors:
                correct = self.normalized_flavors[item]
                self._report_deprecated_flavor_syntax(item, correct)
                return correct, index
            if normalize(item).startswith('in'):
                return item.upper(), index
        return 'IN', len(declaration)

    def _report_deprecated_flavor_syntax(self, deprecated, correct):
        self.parent.report_invalid_syntax(
            "Using '%s' as a FOR loop separator is deprecated. "
            "Use '%s' instead." % (deprecated, correct), level='WARN'
        )

    def is_comment(self):
        return False

    def is_for_loop(self):
        return True

    def as_list(self, indent=False, include_comment=True):
        comments = self.comment.as_list() if include_comment else []
        # TODO: Return 'FOR' in RF 3.2.
        return [': FOR'] + self.vars + [self.flavor] + self.items + comments

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
        return all(value.lower() == 'value' for value in header[1:])


class OldStyleTestAndKeywordTableHeaderMatcher(object):

    def match(self, header):
        if header[1].lower() != 'action':
            return False
        for arg in header[2:]:
            if not arg.lower().startswith('arg'):
                return False
        return True
