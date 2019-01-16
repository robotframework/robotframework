import ast
import os
import re

from robot.errors import DataError
from robot.parsing import TEST_EXTENSIONS
from robot.parsing.newparser import builder
from robot.parsing.newparser.nodes import TestCaseSection
from robot.model import SuiteNamePatterns
from robot.running.model import TestSuite, Keyword, ForLoop, ResourceFile
from robot.utils import abspath
from robot.variables import VariableIterator
from robot.output import LOGGER
from robot.utils import normalize, unic


def create_fixture(data, type):
    if not data or data[0].upper() == 'NONE':
        return None
    return Keyword(name=data[0] if data else None, args=tuple(data[1:]), type=type)


def join_doc(values):
    return ''.join(doc(values))


def doc(values):
    for index, item in enumerate(values):
        yield item
        if index < len(values) - 1:
            yield _joiner_based_on_eol_escapes(item)


def _joiner_based_on_eol_escapes(item):
    _end_of_line_escapes = re.compile(r'(\\+)n?$')
    match = _end_of_line_escapes.search(item)
    if match and len(match.group(1)) % 2 == 1:
        return ''
    return '\n'


class SettingsBuilder(ast.NodeVisitor):
    def __init__(self, suite, test_defaults):
        self.suite = suite
        self.test_defaults = test_defaults

    def visit_DocumentationSetting(self, node):
        self.suite.doc = join_doc(node.value)

    def visit_MetadataSetting(self, node):
        self.suite.metadata[node.name] = join_doc(node.value)

    def visit_SuiteSetupSetting(self, node):
        self.suite.keywords.setup = create_fixture(node.value, 'setup')

    def visit_SuiteTeardownSetting(self, node):
        self.suite.keywords.teardown = create_fixture(node.value, 'teardown')

    def visit_TestSetupSetting(self, node):
        self.test_defaults.setup = node.value

    def visit_TestTeardownSetting(self, node):
        self.test_defaults.teardown = node.value

    def visit_TestTimeoutSetting(self, node):
        self.test_defaults.timeout = node.value

    def visit_DefaultTagsSetting(self, node):
        self.test_defaults.default_tags = node.value

    def visit_ForceTagsSetting(self, node):
        self.test_defaults.force_tags = node.value

    def visit_TestTemplateSetting(self, node):
        self.test_defaults.test_template = node.value

    def visit_ResourceSetting(self, node):
        self.suite.resource.imports.create(type='Resource', name=node.name, args=tuple(node.args))

    def visit_LibrarySetting(self, node):
        args, alias = self._split_possible_alias(node.args)
        self.suite.resource.imports.create(type='Library', name=node.name, args=args, alias=alias)

    def _split_possible_alias(self, args):
        if len(args) > 1 and args[-2] == 'WITH NAME':
            return args[:-2], args[-1]
        return args, None

    def visit_VariablesSetting(self, node):
        self.suite.resource.imports.create(type='Variables', name=node.name, args=tuple(node.args))

    def visit_VariableSection(self, node):
        pass

    def visit_TestCaseSection(self, node):
        pass

    def visit_KeywordSection(self, node):
        pass


class SuiteBuilder(ast.NodeVisitor):
    def __init__(self, suite, test_defaults):
        self.suite = suite
        self.test_defaults = test_defaults

    def visit_TestCase(self, node):
        TestCaseBuilder(self.suite, self.test_defaults).visit(node)

    def visit_Keyword(self, node):
        KeywordBuilder(self.suite.resource).visit(node)

    def visit_Variable(self, node):
        name = node.name
        if node.name.endswith('='):
            name = name[:-1].rstrip()
        self.suite.resource.variables.create(name=name, value=node.value)


class ResourceBuilder(ast.NodeVisitor):
    def __init__(self, resource):
        self.resource = resource

    def visit_ResourceSetting(self, node):
        self.resource.imports.create(type='Resource', name=node.name, args=tuple(node.args))

    def visit_LibrarySetting(self, node):
        self.resource.imports.create(type='Library', name=node.name, args=tuple(node.args))

    def visit_VariablesSetting(self, node):
        self.resource.imports.create(type='Variables', name=node.name, args=tuple(node.args))

    def visit_Keyword(self, node):
        KeywordBuilder(self.resource).visit(node)

    def visit_Variable(self, node):
        name = node.name
        if node.name.endswith('='):
            name = name[:-1].rstrip()
        self.resource.variables.create(name=name, value=node.value)

    def visit_DocumentationSetting(self, node):
        self.resource.doc = join_doc(node.value)


class TestCaseBuilder(ast.NodeVisitor):

    def __init__(self, suite, defaults):
        self.suite = suite
        self.settings = TestSettings(defaults)
        self.test = None

    def visit_TestCase(self, node):
        self.test = self.suite.tests.create(name=node.name)
        self.generic_visit(node)
        self.settings.set_test_values(self.test)
        template = self.settings.get_template()
        if template:
            self._set_template(self.test, template[0])
            self.test.template = template[0]

    def _set_template(self, parent, template):
        for kw in parent.keywords:
            if kw.type == kw.FOR_LOOP_TYPE:
                self._set_template(kw, template)
            elif kw.type == kw.KEYWORD_TYPE:
                name, args = self._format_template(template, kw.args)
                kw.name = name
                kw.args = args

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

    def visit_ForLoop(self, node):
        for_loop = ForLoop(node.variables, node.values, node.flavor)
        ForLoopBuilder(for_loop).visit(node)
        self.test.keywords.append(for_loop)

    def visit_TemplateArguments(self, node):
        self.test.keywords.append(Keyword(args=node.args))

    def visit_DocumentationSetting(self, node):
        self.test.doc = join_doc(node.value)

    def visit_SetupSetting(self, node):
        self.settings.setup = node.value

    def visit_TeardownSetting(self, node):
        self.settings.teardown = node.value

    def visit_TimeoutSetting(self, node):
        self.settings.timeout = node.value

    def visit_TagsSetting(self, node):
        self.settings.tags = node.value

    def visit_TemplateSetting(self, node):
        self.settings.template = node.value

    def visit_KeywordCall(self, node):
        self.test.keywords.create(name=node.keyword, args=node.args, assign=node.assign or [])


class KeywordBuilder(ast.NodeVisitor):
    def __init__(self, resource):
        self.resource = resource
        self.kw = None
        self.teardown = None

    def visit_Keyword(self, node):
        self.kw = self.resource.keywords.create(name=node.name)
        self.generic_visit(node)
        if self.teardown:
            self.kw.keywords.teardown = create_fixture(self.teardown, 'teardown')

    def visit_DocumentationSetting(self, node):
        self.kw.doc = join_doc(node.value)

    def visit_ArgumentsSetting(self, node):
        self.kw.args = node.value

    def visit_TagsSetting(self, node):
        self.kw.tags = node.value

    def visit_ReturnSetting(self, node):
        self.kw.return_ = node.value

    def visit_TimeoutSetting(self, node):
        self.kw.timeout = node.value

    def visit_TeardownSetting(self, node):
        self.teardown = node.value

    def visit_KeywordCall(self, node):
        self.kw.keywords.create(name=node.keyword, args=node.args, assign=node.assign or [])

    def visit_ForLoop(self, node):
        for_loop = ForLoop(node.variables, node.values, node.flavor)
        ForLoopBuilder(for_loop).visit(node)
        self.kw.keywords.append(for_loop)


class ForLoopBuilder(ast.NodeVisitor):
    def __init__(self, for_loop):
        self.for_loop = for_loop

    def visit_KeywordCall(self, node):
        self.for_loop.keywords.create(name=node.keyword, args=node.args, assign=node.assign or [])

    def visit_TemplateArguments(self, node):
        self.for_loop.keywords.append(Keyword(args=node.args))


class TestDefaults(object):

    def __init__(self, parent_defaults):
        self.setup = None
        self.teardown = None
        self.timeout = None
        self.force_tags = None
        self.default_tags = None
        self.test_template = None
        self.parent_defaults = parent_defaults

    def get_force_tags(self):
        force_tags = self.force_tags or []
        return force_tags + ((self.parent_defaults and self.parent_defaults.get_force_tags()) or [])

    def get_setup(self):
        return self.setup or (self.parent_defaults and self.parent_defaults.get_setup())

    def get_teardown(self):
        return self.teardown or (self.parent_defaults and self.parent_defaults.get_teardown())

    def get_timeout(self):
        return self.timeout or (self.parent_defaults and self.parent_defaults.get_timeout())


class TestSettings(object):

    def __init__(self, defaults):
        self.defaults = defaults
        self.setup = None
        self.teardown = None
        self.timeout = None
        self.template = None
        self.tags = None

    def get_template(self):
        template = self.template if self.template is not None else self.defaults.test_template
        return template if template and template[0].upper() != 'NONE' else None

    def set_test_values(self, test):
        self.set_setup(test)
        self.set_teardown(test)
        self.set_timout(test)
        self.set_tags(test)

    def set_setup(self, test):
        setup = self.setup or self.defaults.get_setup()
        if setup:
             test.keywords.setup = create_fixture(setup, type='setup')

    def set_teardown(self, test):
        teardown = self.teardown or self.defaults.get_teardown()
        if teardown:
            test.keywords.teardown = create_fixture(teardown, type='teardown')

    def set_timout(self, test):
        timeout = self.timeout or self.defaults.get_timeout()
        if timeout:
            test.timeout = timeout

    def set_tags(self, test):
        default_tags = (self.tags or self.defaults.default_tags) or []
        test.tags = default_tags + self.defaults.get_force_tags()


class TestSuiteBuilder(object):
    ignored_prefixes = ('_', '.')
    ignored_dirs = ('CVS',)

    def __init__(self, include_suites=None, extension=None, rpa=None):
        self.rpa = rpa
        self._rpa_not_given = rpa is None
        self.include_suites = include_suites
        self.extension = extension

    def build(self, *paths):
        """
        :param paths: Paths to test data files or directories.
        :return: :class:`~robot.running.model.TestSuite` instance.
        """
        if not paths:
            raise DataError('One or more source paths required.')
        if len(paths) == 1:
            return self._parse_and_build(paths[0], include_suites=self.include_suites, include_extensions=self.extension)
        root = TestSuite()
        for path in paths:
            root.suites.append(self._parse_and_build(path))
        root.rpa = self.rpa
        return root

    def _get_extensions(self, extension):
        if not extension:
            return None
        extensions = set(ext.lower().lstrip('.') for ext in extension.split(':'))
        if not all(ext in TEST_EXTENSIONS for ext in extensions):
            raise DataError("Invalid extension to limit parsing '%s'." % extension)
        return extensions

    def _parse_and_build(self, path, parent_defaults=None, include_suites=None, include_extensions=None):
        path = abspath(path)
        name = format_name(path)
        if os.path.isdir(path):
            LOGGER.info("Parsing directory '%s'." % path)
            include_suites = self._get_include_suites(path, include_suites)
            init_file, children = self._get_children(path, include_extensions, include_suites)
            defaults = parent_defaults
            if init_file:
                suite, defaults = self._build_suite(init_file, name, parent_defaults)
            else:
                suite = TestSuite(name=name, source=path)
            for c in children:
                suite.suites.append(self._parse_and_build(c, defaults, include_suites, include_extensions))
        else:
            LOGGER.info("Parsing file '%s'." % path)
            suite, _ = self._build_suite(path, name, parent_defaults)
        suite.rpa = self.rpa
        suite.remove_empty_suites()
        return suite

    def _build_suite(self, source, name, parent_defaults):
        data = self._parse(source)
        test_section = self._get_test_section(data)
        if self._rpa_not_given and test_section:
            self._set_execution_mode(test_section, source)
        suite = TestSuite(name=name, source=source)
        defaults = TestDefaults(parent_defaults)
        if data:
            #print(ast.dump(data))
            SettingsBuilder(suite, defaults).visit(data)
            SuiteBuilder(suite, defaults).visit(data)
        return suite, defaults

    def _get_test_section(self, data):
        test_sections = [s for s in data.sections if isinstance(s, TestCaseSection)]
        return test_sections[0] if test_sections else None

    def _set_execution_mode(self, test_section, source):
        rpa = test_section.header.lower() in ('task', 'tasks')
        if self.rpa is None:
            self.rpa = rpa
        elif self.rpa is not rpa:
            this, that = ('tasks', 'tests') if rpa else ('tests', 'tasks')
            raise DataError("Conflicting execution modes. File '%s' has %s "
                            "but files parsed earlier have %s. Fix headers "
                            "or use '--rpa' or '--norpa' options to set the "
                            "execution mode explicitly."
                            % (source, this, that))

    def _parse(self, path):
        try:
            return builder.get_test_case_file_ast(path)
        except DataError as err:
            raise DataError("Parsing '%s' failed: %s" % (path, err.message))

    def _get_include_suites(self, path, incl_suites):
        if not incl_suites:
            return None
        if not isinstance(incl_suites, SuiteNamePatterns):
            incl_suites = SuiteNamePatterns(
                self._create_included_suites(incl_suites))
        # If a directory is included, also all its children should be included.
        if self._is_in_included_suites(os.path.basename(path), incl_suites):
            return None
        return incl_suites

    def _create_included_suites(self, incl_suites):
        for suite in incl_suites:
            yield suite
            while '.' in suite:
                suite = suite.split('.', 1)[1]
                yield suite

    def _get_children(self, dirpath, incl_extensions=None, incl_suites=None):
        init_file = None
        children = []
        for path, is_init_file in self._list_dir(dirpath, incl_extensions,
                                                 incl_suites):
            if is_init_file:
                if not init_file:
                    init_file = path
                else:
                    LOGGER.error("Ignoring second test suite init file '%s'." % path)
            else:
                children.append(path)
        return init_file, children

    def _list_dir(self, dir_path, incl_extensions, incl_suites):
        # os.listdir returns Unicode entries when path is Unicode
        dir_path = unic(dir_path)
        names = os.listdir(dir_path)
        for name in sorted(names, key=lambda item: item.lower()):
            name = unic(name)  # needed to handle nfc/nfd normalization on OSX
            path = os.path.join(dir_path, name)
            base, ext = os.path.splitext(name)
            ext = ext[1:].lower()
            if self._is_init_file(path, base, ext, incl_extensions):
                yield path, True
            elif self._is_included(path, base, ext, incl_extensions, incl_suites):
                yield path, False
            else:
                LOGGER.info("Ignoring file or directory '%s'." % path)

    def _is_init_file(self, path, base, ext, incl_extensions):
        return (base.lower() == '__init__' and
                self._extension_is_accepted(ext, incl_extensions) and
                os.path.isfile(path))

    def _extension_is_accepted(self, ext, incl_extensions):
        if incl_extensions:
            return ext in incl_extensions
        return ext in TEST_EXTENSIONS

    def _is_included(self, path, base, ext, incl_extensions, incl_suites):
        if base.startswith(self.ignored_prefixes):
            return False
        if os.path.isdir(path):
            return base not in self.ignored_dirs or ext
        if not self._extension_is_accepted(ext, incl_extensions):
            return False
        return self._is_in_included_suites(base, incl_suites)

    def _is_in_included_suites(self, name, incl_suites):
        if not incl_suites:
            return True
        return incl_suites.match(self._split_prefix(name))

    def _split_prefix(self, name):
        return name.split('__', 1)[-1]


class ResourceFileBuilder(object):

    def build(self, path):
        resource = ResourceFile(source=path)
        data = builder.get_resource_file_ast(path)
        if data.sections:
            ResourceBuilder(resource).visit(data)
        else:
            LOGGER.warn("Imported resource file '%s' is empty." % path)
        return resource


def format_name(source):
    def strip_possible_prefix_from_name(name):
        return name.split('__', 1)[-1]

    def format_name(name):
        name = strip_possible_prefix_from_name(name)
        name = name.replace('_', ' ').strip()
        return name.title() if name.islower() else name

    if os.path.isdir(source):
        basename = os.path.basename(source)
    else:
        basename = os.path.splitext(os.path.basename(source))[0]
    return format_name(basename)
