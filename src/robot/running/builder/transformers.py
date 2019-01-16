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

from ..model import ForLoop
from .testsettings import TestSettings


class SettingsBuilder(ast.NodeVisitor):

    def __init__(self, suite, test_defaults):
        self.suite = suite
        self.test_defaults = test_defaults

    def visit_DocumentationSetting(self, node):
        self.suite.doc = node.value

    def visit_MetadataSetting(self, node):
        self.suite.metadata[node.name] = node.value

    def visit_SuiteSetupSetting(self, node):
        if node.name:
            self.suite.keywords.create_setup(name=node.name, args=node.args)

    def visit_SuiteTeardownSetting(self, node):
        if node.name:
            self.suite.keywords.create_teardown(name=node.name, args=node.args)

    def visit_TestSetupSetting(self, node):
        self.test_defaults.setup = node

    def visit_TestTeardownSetting(self, node):
        self.test_defaults.teardown = node

    def visit_TestTimeoutSetting(self, node):
        self.test_defaults.timeout = node

    def visit_DefaultTagsSetting(self, node):
        # TODO: should node be always given to test_defaults?
        self.test_defaults.default_tags = node.value

    def visit_ForceTagsSetting(self, node):
        self.test_defaults.force_tags = node.value

    def visit_TestTemplateSetting(self, node):
        self.test_defaults.test_template = node

    def visit_ResourceSetting(self, node):
        self.suite.resource.imports.create(type='Resource', name=node.name,
                                           args=tuple(node.args))

    def visit_LibrarySetting(self, node):
        self.suite.resource.imports.create(type='Library', name=node.name,
                                           args=node.args, alias=node.alias)

    def visit_VariablesSetting(self, node):
        self.suite.resource.imports.create(type='Variables', name=node.name,
                                           args=tuple(node.args))

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
        self.resource.imports.create(type='Resource', name=node.name,
                                     args=tuple(node.args))

    def visit_LibrarySetting(self, node):
        self.resource.imports.create(type='Library', name=node.name,
                                           args=node.args, alias=node.alias)


    def visit_VariablesSetting(self, node):
        self.resource.imports.create(type='Variables', name=node.name,
                                     args=tuple(node.args))

    def visit_Keyword(self, node):
        KeywordBuilder(self.resource).visit(node)

    def visit_Variable(self, node):
        name = node.name
        if node.name.endswith('='):
            name = name[:-1].rstrip()
        self.resource.variables.create(name=name, value=node.value)

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
        self._set_settings(self.settings)

    def _set_settings(self, settings):
        if settings.setup and settings.setup.name:
            self.test.keywords.create_setup(name=settings.setup.name,
                                            args=settings.setup.args)
        if settings.teardown and settings.teardown.name:
            self.test.keywords.create_teardown(name=settings.teardown.name,
                                               args=settings.teardown.args)
        self.test.timeout = settings.timeout
        self.test.tags = settings.tags
        if settings.template:
            self.test.template = settings.template
            self._set_template(self.test, settings.template)

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
        self.test.keywords.create(args=node.args)

    def visit_DocumentationSetting(self, node):
        self.test.doc = node.value

    def visit_SetupSetting(self, node):
        self.settings.setup = node

    def visit_TeardownSetting(self, node):
        self.settings.teardown = node

    def visit_TimeoutSetting(self, node):
        self.settings.timeout = node

    def visit_TagsSetting(self, node):
        self.settings.tags = node.value

    def visit_TemplateSetting(self, node):
        self.settings.template = node

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
        if self.teardown and self.teardown.name:
            self.kw.keywords.create_teardown(name=self.teardown.name,
                                             args=self.teardown.args)

    def visit_DocumentationSetting(self, node):
        self.kw.doc = node.value

    def visit_ArgumentsSetting(self, node):
        self.kw.args = node.value

    def visit_TagsSetting(self, node):
        self.kw.tags = node.value

    def visit_ReturnSetting(self, node):
        self.kw.return_ = node.value

    def visit_TimeoutSetting(self, node):
        self.kw.timeout = node.value

    def visit_TeardownSetting(self, node):
        self.teardown = node

    def visit_KeywordCall(self, node):
        self.kw.keywords.create(name=node.keyword, args=node.args,
                                assign=node.assign)

    def visit_ForLoop(self, node):
        for_loop = ForLoop(node.variables, node.values, node.flavor)
        ForLoopBuilder(for_loop).visit(node)
        self.kw.keywords.append(for_loop)


class ForLoopBuilder(ast.NodeVisitor):
    def __init__(self, for_loop):
        self.for_loop = for_loop

    def visit_KeywordCall(self, node):
        self.for_loop.keywords.create(name=node.keyword, args=node.args,
                                      assign=node.assign)

    def visit_TemplateArguments(self, node):
        self.for_loop.keywords.create(args=node.args)
