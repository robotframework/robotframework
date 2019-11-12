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

import ast

from robot.variables import VariableIterator

from ..model import ForLoop, Keyword
from .testsettings import TestSettings


def fixture(node, fixture_type):
    if node.name is None:
        return None
    return Keyword(node.name, args=node.args, type=fixture_type)


class SettingsBuilder(ast.NodeVisitor):

    def __init__(self, suite, test_defaults):
        self.suite = suite
        self.test_defaults = test_defaults

    def visit_DocumentationSetting(self, node):
        self.suite.doc = node.value

    def visit_MetadataSetting(self, node):
        self.suite.metadata[node.name] = node.value

    def visit_SuiteSetupSetting(self, node):
        self.suite.keywords.setup = fixture(node, Keyword.SETUP_TYPE)

    def visit_SuiteTeardownSetting(self, node):
        self.suite.keywords.teardown = fixture(node, Keyword.TEARDOWN_TYPE)

    def visit_TestSetupSetting(self, node):
        self.test_defaults.setup = fixture(node, Keyword.SETUP_TYPE)

    def visit_TestTeardownSetting(self, node):
        self.test_defaults.teardown = fixture(node, Keyword.TEARDOWN_TYPE)

    def visit_TestTimeoutSetting(self, node):
        self.test_defaults.timeout = node.value

    def visit_DefaultTagsSetting(self, node):
        self.test_defaults.default_tags = node.values

    def visit_ForceTagsSetting(self, node):
        self.test_defaults.force_tags = node.values

    def visit_TestTemplateSetting(self, node):
        self.test_defaults.template = node.value

    def visit_ResourceSetting(self, node):
        self.suite.resource.imports.create(type='Resource', name=node.name,
                                           args=node.args)

    def visit_LibrarySetting(self, node):
        self.suite.resource.imports.create(type='Library', name=node.name,
                                           args=node.args, alias=node.alias)

    def visit_VariablesSetting(self, node):
        self.suite.resource.imports.create(type='Variables', name=node.name,
                                           args=node.args)

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
        self.suite.resource.variables.create(name=node.name, value=node.value)


class ResourceBuilder(ast.NodeVisitor):

    def __init__(self, resource):
        self.resource = resource

    def visit_ResourceSetting(self, node):
        self.resource.imports.create(type='Resource', name=node.name,
                                     args=node.args)

    def visit_LibrarySetting(self, node):
        self.resource.imports.create(type='Library', name=node.name,
                                     args=node.args, alias=node.alias)


    def visit_VariablesSetting(self, node):
        self.resource.imports.create(type='Variables', name=node.name,
                                     args=node.args)

    def visit_Keyword(self, node):
        KeywordBuilder(self.resource).visit(node)

    def visit_Variable(self, node):
        self.resource.variables.create(name=node.name, value=node.value)

    def visit_DocumentationSetting(self, node):
        self.resource.doc = node.value


class TestCaseBuilder(ast.NodeVisitor):

    def __init__(self, suite, defaults):
        self.suite = suite
        self.settings = TestSettings(defaults)
        self.test = None

    def visit_TestCase(self, node):
        self.test = self.suite.tests.create(name=node.name)
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
        # Header and end used only for deprecation purposes. Remove in RF 3.3!
        loop = ForLoop(node.variables, node.values, node.flavor,
                       node._header, node._end)
        ForLoopBuilder(loop).visit(node)
        self.test.keywords.append(loop)

    def visit_TemplateArguments(self, node):
        self.test.keywords.create(args=node.args)

    def visit_DocumentationSetting(self, node):
        self.test.doc = node.value

    def visit_SetupSetting(self, node):
        self.settings.setup = fixture(node, Keyword.SETUP_TYPE)

    def visit_TeardownSetting(self, node):
        self.settings.teardown = fixture(node, Keyword.TEARDOWN_TYPE)

    def visit_TimeoutSetting(self, node):
        self.settings.timeout = node.value

    def visit_TagsSetting(self, node):
        self.settings.tags = node.values

    def visit_TemplateSetting(self, node):
        self.settings.template = node.value

    def visit_KeywordCall(self, node):
        self.test.keywords.create(name=node.keyword, args=node.args,
                                  assign=node.assign)


class KeywordBuilder(ast.NodeVisitor):

    def __init__(self, resource):
        self.resource = resource
        self.kw = None
        self.teardown = None

    def visit_Keyword(self, node):
        self.kw = self.resource.keywords.create(name=node.name)
        self.generic_visit(node)
        self.kw.keywords.teardown = self.teardown

    def visit_DocumentationSetting(self, node):
        self.kw.doc = node.value

    def visit_ArgumentsSetting(self, node):
        self.kw.args = node.values

    def visit_TagsSetting(self, node):
        self.kw.tags = node.values

    def visit_ReturnSetting(self, node):
        self.kw.return_ = node.values

    def visit_TimeoutSetting(self, node):
        self.kw.timeout = node.value

    def visit_TeardownSetting(self, node):
        self.teardown = fixture(node, Keyword.TEARDOWN_TYPE)

    def visit_KeywordCall(self, node):
        self.kw.keywords.create(name=node.keyword, args=node.args,
                                assign=node.assign)

    def visit_ForLoop(self, node):
        # Header and end used only for deprecation purposes. Remove in RF 3.3!
        loop = ForLoop(node.variables, node.values, node.flavor,
                       node._header, node._end)
        ForLoopBuilder(loop).visit(node)
        self.kw.keywords.append(loop)


class ForLoopBuilder(ast.NodeVisitor):

    def __init__(self, for_loop):
        self.for_loop = for_loop

    def visit_KeywordCall(self, node):
        self.for_loop.keywords.create(name=node.keyword, args=node.args,
                                      assign=node.assign)

    def visit_TemplateArguments(self, node):
        self.for_loop.keywords.create(args=node.args)
