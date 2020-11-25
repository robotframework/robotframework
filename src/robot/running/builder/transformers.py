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

from robot.parsing import Token
from robot.variables import VariableIterator

from ..model import For, If
from .testsettings import TestSettings


class SettingsBuilder(NodeVisitor):

    def __init__(self, suite, test_defaults):
        self.suite = suite
        self.test_defaults = test_defaults

    def visit_Documentation(self, node):
        self.suite.doc = node.value

    def visit_Metadata(self, node):
        self.suite.metadata[node.name] = node.value

    def visit_SuiteSetup(self, node):
        self.suite.setup.config(name=node.name, args=node.args,
                                lineno=node.lineno)

    def visit_SuiteTeardown(self, node):
        self.suite.teardown.config(name=node.name, args=node.args,
                                   lineno=node.lineno)

    def visit_TestSetup(self, node):
        self.test_defaults.setup = {
            'name': node.name, 'args': node.args, 'lineno': node.lineno
        }

    def visit_TestTeardown(self, node):
        self.test_defaults.teardown = {
            'name': node.name, 'args': node.args, 'lineno': node.lineno
        }

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
        self.suite.resource.variables.create(name=node.name,
                                             value=node.value,
                                             lineno=node.lineno,
                                             error=format_error(node.errors))

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
        self.resource.variables.create(name=node.name,
                                       value=node.value,
                                       lineno=node.lineno,
                                       error=format_error(node.errors))

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
        test.setup.config(**settings.setup)
        test.teardown.config(**settings.teardown)
        test.timeout = settings.timeout
        test.tags = settings.tags
        if settings.template:
            test.template = settings.template
            self._set_template(test, settings.template)

    def _set_template(self, parent, template):
        for kw in parent.keywords:
            if kw.type == kw.FOR_LOOP_TYPE:
                self._set_template(kw, template)
            elif kw.type == kw.IF_TYPE:
                branch = kw
                while branch:
                    self._set_template(branch, template)
                    branch = branch.orelse
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

    def visit_For(self, node):
        loop = ForBuilder().build(node)
        self.test.keywords.append(loop)

    def visit_If(self, node):
        ifblock = IfBuilder().build(node)
        self.test.keywords.append(ifblock)

    def visit_TemplateArguments(self, node):
        self.test.keywords.create(args=node.args, lineno=node.lineno)

    def visit_Documentation(self, node):
        self.test.doc = node.value

    def visit_Setup(self, node):
        self.settings.setup = {
            'name': node.name, 'args': node.args, 'lineno': node.lineno
        }

    def visit_Teardown(self, node):
        self.settings.teardown = {
            'name': node.name, 'args': node.args, 'lineno': node.lineno
        }

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
        if self.teardown is not None:
            self.kw.teardown.config(**self.teardown)

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
        self.teardown = {
            'name': node.name, 'args': node.args, 'lineno': node.lineno
        }

    def visit_KeywordCall(self, node):
        self.kw.keywords.create(name=node.keyword, args=node.args,
                                assign=node.assign, lineno=node.lineno)

    def visit_For(self, node):
        loop = ForBuilder().build(node)
        self.kw.keywords.append(loop)

    def visit_If(self, node):
        ifblock = IfBuilder().build(node)
        self.kw.keywords.append(ifblock)


class ForBuilder(NodeVisitor):

    def __init__(self):
        self.loop = None

    def build(self, node):
        self.loop = For(node.variables, node.flavor, node.values,
                        node.lineno, error=self._get_error(node))
        for child_node in node.body:
            self.visit(child_node)
        return self.loop

    def _get_error(self, node):
        errors = node.header.errors + node.errors
        if node.end:
            errors += node.end.errors
        return format_error(errors)

    def visit_KeywordCall(self, node):
        self.loop.keywords.create(name=node.keyword, args=node.args,
                                  assign=node.assign, lineno=node.lineno)

    def visit_TemplateArguments(self, node):
        self.loop.keywords.create(args=node.args, lineno=node.lineno)

    def visit_For(self, node):
        loop = ForBuilder().build(node)
        self.loop.keywords.append(loop)

    def visit_If(self, node):
        ifblock = IfBuilder().build(node)
        self.loop.keywords.append(ifblock)


class IfBuilder(NodeVisitor):

    def __init__(self):
        self.block = None

    def build(self, node):
        self.block = If(node.condition, lineno=node.lineno,
                        error=self._get_error(node), type=self._get_type(node))
        for child_node in node.body:
            self.visit(child_node)
        if node.orelse:
            self.block.orelse = IfBuilder().build(node.orelse)
        return self.block

    def _get_error(self, node):
        return format_error(self._get_errors(node))

    def _get_errors(self, node):
        errors = node.header.errors + node.errors
        if node.orelse:
            errors += self._get_errors(node.orelse)
        if node.end:
            errors += node.end.errors
        return errors

    def _get_type(self, node):
        return {Token.IF: If.IF_TYPE,
                Token.ELSE_IF: If.ELSE_IF_TYPE,
                Token.ELSE: If.ELSE_TYPE}[node.type]

    def visit_KeywordCall(self, node):
        self.block.keywords.create(name=node.keyword, args=node.args,
                                   assign=node.assign, lineno=node.lineno)

    def visit_TemplateArguments(self, node):
        self.block.keywords.create(args=node.args, lineno=node.lineno)

    def visit_If(self, node):
        block = IfBuilder().build(node)
        self.block.keywords.append(block)

    def visit_For(self, node):
        loop = ForBuilder().build(node)
        self.block.keywords.append(loop)


def format_error(errors):
    if not errors:
        return None
    if len(errors) == 1:
        return errors[0]
    return '\n- '.join(('Multiple errors:',) + errors)
