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

from ast import NodeVisitor

from robot.variables import VariableIterator

from ..model import ForLoop, Keyword
from .testsettings import TestSettings


def fixture(node, fixture_type):
    if node.name is None:
        return None
    return Keyword(node.name, args=node.args, type=fixture_type,
                   lineno=node.lineno)


class SettingsBuilder(NodeVisitor):

    def __init__(self, suite, test_defaults):
        self.suite = suite
        self.test_defaults = test_defaults

    def visit_Documentation(self, node):
        self.suite.doc = node.value

    def visit_Metadata(self, node):
        self.suite.metadata[node.name] = node.value

    def visit_SuiteSetup(self, node):
        self.suite.keywords.setup = fixture(node, Keyword.SETUP_TYPE)

    def visit_SuiteTeardown(self, node):
        self.suite.keywords.teardown = fixture(node, Keyword.TEARDOWN_TYPE)

    def visit_TestSetup(self, node):
        self.test_defaults.setup = fixture(node, Keyword.SETUP_TYPE)

    def visit_TestTeardown(self, node):
        self.test_defaults.teardown = fixture(node, Keyword.TEARDOWN_TYPE)

    def visit_TestTimeout(self, node):
        self.test_defaults.timeout = node.value

    def visit_DefaultTags(self, node):
        self.test_defaults.default_tags = node.values

    def visit_ForceTags(self, node):
        self.test_defaults.force_tags = node.values

    def visit_TestTemplate(self, node):
        self.test_defaults.template = node.value

    def visit_ResourceImport(self, node):
        self.suite.resource.imports.create(type='Resource', name=node.name,
                                           lineno=node.lineno)

    def visit_LibraryImport(self, node):
        self.suite.resource.imports.create(type='Library', name=node.name,
                                           args=node.args, alias=node.alias,
                                           lineno=node.lineno)

    def visit_VariablesImport(self, node):
        self.suite.resource.imports.create(type='Variables', name=node.name,
                                           args=node.args, lineno=node.lineno)

    def visit_VariableSection(self, node):
        pass

    def visit_TestCaseSection(self, node):
        pass

    def visit_KeywordSection(self, node):
        pass


class SuiteBuilder(NodeVisitor):

    def __init__(self, suite, test_defaults):
        self.suite = suite
        self.test_defaults = test_defaults

    def visit_SettingSection(self, node):
        pass

    def visit_Variable(self, node):
        self.suite.resource.variables.create(name=node.name, value=node.value,
                                             lineno=node.lineno, error=node.error)

    def visit_TestCase(self, node):
        TestCaseBuilder(self.suite, self.test_defaults).visit(node)

    def visit_Keyword(self, node):
        KeywordBuilder(self.suite.resource).visit(node)


class ResourceBuilder(NodeVisitor):

    def __init__(self, resource):
        self.resource = resource

    def visit_Documentation(self, node):
        self.resource.doc = node.value

    def visit_LibraryImport(self, node):
        self.resource.imports.create(type='Library', name=node.name,
                                     args=node.args, alias=node.alias,
                                     lineno=node.lineno)

    def visit_ResourceImport(self, node):
        self.resource.imports.create(type='Resource', name=node.name,
                                     lineno=node.lineno)

    def visit_VariablesImport(self, node):
        self.resource.imports.create(type='Variables', name=node.name,
                                     args=node.args, lineno=node.lineno)

    def visit_Variable(self, node):
        self.resource.variables.create(name=node.name, value=node.value,
                                       lineno=node.lineno, error=node.error)
    def visit_Keyword(self, node):
        KeywordBuilder(self.resource).visit(node)


class TestCaseBuilder(NodeVisitor):

    def __init__(self, suite, defaults):
        self.suite = suite
        self.settings = TestSettings(defaults)
        self.test = None

    def visit_TestCase(self, node):
        self.test = self.suite.tests.create(name=node.name, lineno=node.lineno)
        self.generic_visit(node)
        self._set_settings(self.test, self.settings)

    def _set_settings(self, test, settings):
        test.keywords.setup = settings.setup
        test.keywords.teardown = settings.teardown
        test.timeout = settings.timeout
        test.tags = settings.tags
        if settings.template:
            test.template = settings.template
            self._set_template(test, settings.template)

    def _set_template(self, parent, template):
        for kw in parent.keywords:
            if kw.type == kw.FOR_LOOP_TYPE:
                self._set_template(kw, template)
            elif kw.type == kw.KEYWORD_TYPE:
                name, args = self._format_template(template, kw.args)
                kw.name = name
                kw.args = args

    def _format_template(self, template, arguments):
        variables = VariableIterator(template, identifiers='$')
        count = len(variables)
        if count == 0 or count != len(arguments):
            return template, arguments
        temp = []
        for (before, _, after), arg in zip(variables, arguments):
            temp.extend([before, arg])
        temp.append(after)
        return ''.join(temp), ()

    def visit_ForLoop(self, node):
        # Header and end used only for deprecation purposes. Remove in RF 3.3!
        loop = ForLoop(node.variables, node.values, node.flavor, node.lineno,
                       node._header, node._end)
        ForLoopBuilder(loop).visit(node)
        self.test.keywords.append(loop)

    def visit_TemplateArguments(self, node):
        self.test.keywords.create(args=node.args, lineno=node.lineno)

    def visit_Documentation(self, node):
        self.test.doc = node.value

    def visit_Setup(self, node):
        self.settings.setup = fixture(node, Keyword.SETUP_TYPE)

    def visit_Teardown(self, node):
        self.settings.teardown = fixture(node, Keyword.TEARDOWN_TYPE)

    def visit_Timeout(self, node):
        self.settings.timeout = node.value

    def visit_Tags(self, node):
        self.settings.tags = node.values

    def visit_Template(self, node):
        self.settings.template = node.value

    def visit_KeywordCall(self, node):
        self.test.keywords.create(name=node.keyword, args=node.args,
                                  assign=node.assign, lineno=node.lineno)


class KeywordBuilder(NodeVisitor):

    def __init__(self, resource):
        self.resource = resource
        self.kw = None
        self.teardown = None

    def visit_Keyword(self, node):
        self.kw = self.resource.keywords.create(name=node.name,
                                                lineno=node.lineno)
        self.generic_visit(node)
        self.kw.keywords.teardown = self.teardown

    def visit_Documentation(self, node):
        self.kw.doc = node.value

    def visit_Arguments(self, node):
        self.kw.args = node.values

    def visit_Tags(self, node):
        self.kw.tags = node.values

    def visit_Return(self, node):
        self.kw.return_ = node.values

    def visit_Timeout(self, node):
        self.kw.timeout = node.value

    def visit_Teardown(self, node):
        self.teardown = fixture(node, Keyword.TEARDOWN_TYPE)

    def visit_KeywordCall(self, node):
        self.kw.keywords.create(name=node.keyword, args=node.args,
                                assign=node.assign, lineno=node.lineno)

    def visit_ForLoop(self, node):
        # Header and end used only for deprecation purposes. Remove in RF 3.3!
        loop = ForLoop(node.variables, node.values, node.flavor, node.lineno,
                       node._header, node._end)
        ForLoopBuilder(loop).visit(node)
        self.kw.keywords.append(loop)


class ForLoopBuilder(NodeVisitor):

    def __init__(self, loop):
        self.loop = loop

    def visit_KeywordCall(self, node):
        self.loop.keywords.create(name=node.keyword, args=node.args,
                                  assign=node.assign, lineno=node.lineno)

    def visit_TemplateArguments(self, node):
        self.loop.keywords.create(args=node.args, lineno=node.lineno)
