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
        for item in parent.body:
            if item.type == item.FOR:
                self._set_template(item, template)
            elif item.type == item.IF_ELSE_ROOT:
                for branch in item.body:
                    self._set_template(branch, template)
            elif item.type == item.KEYWORD:
                name, args = self._format_template(template, item.args)
                item.name = name
                item.args = args

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
        ForBuilder(self.test).build(node)

    def visit_If(self, node):
        IfBuilder(self.test).build(node)

    def visit_TemplateArguments(self, node):
        self.test.body.create_keyword(args=node.args, lineno=node.lineno)

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
        self.test.body.create_keyword(name=node.keyword, args=node.args,
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
        self.kw.body.create_keyword(name=node.keyword, args=node.args,
                                    assign=node.assign, lineno=node.lineno)

    def visit_For(self, node):
        ForBuilder(self.kw).build(node)

    def visit_If(self, node):
        IfBuilder(self.kw).build(node)


class ForBuilder(NodeVisitor):

    def __init__(self, parent):
        self.parent = parent
        self.model = None

    def build(self, node):
        error = format_error(self._get_errors(node))
        self.model = self.parent.body.create_for(
            node.variables, node.flavor, node.values, lineno=node.lineno, error=error
        )
        for step in node.body:
            self.visit(step)
        return self.model

    def _get_errors(self, node):
        errors = node.header.errors + node.errors
        if node.end:
            errors += node.end.errors
        return errors

    def visit_KeywordCall(self, node):
        self.model.body.create_keyword(name=node.keyword, args=node.args,
                                       assign=node.assign, lineno=node.lineno)

    def visit_TemplateArguments(self, node):
        self.model.body.create_keyword(args=node.args, lineno=node.lineno)

    def visit_For(self, node):
        ForBuilder(self.model).build(node)

    def visit_If(self, node):
        IfBuilder(self.model).build(node)


class IfBuilder(NodeVisitor):

    def __init__(self, parent):
        self.parent = parent
        self.model = None

    def build(self, node):
        model = self.parent.body.create_if(lineno=node.lineno,
                                           error=format_error(self._get_errors(node)))
        while node:
            self.model = model.body.create_branch(node.type, node.condition,
                                                  lineno=node.lineno)
            for step in node.body:
                self.visit(step)
            node = node.orelse
        return model

    def _get_errors(self, node):
        errors = node.header.errors + node.errors
        if node.orelse:
            errors += self._get_errors(node.orelse)
        if node.end:
            errors += node.end.errors
        return errors

    def visit_KeywordCall(self, node):
        self.model.body.create_keyword(name=node.keyword, args=node.args,
                                       assign=node.assign, lineno=node.lineno)

    def visit_TemplateArguments(self, node):
        self.model.body.create_keyword(args=node.args, lineno=node.lineno)

    def visit_If(self, node):
        IfBuilder(self.model).build(node)

    def visit_For(self, node):
        ForBuilder(self.model).build(node)


def format_error(errors):
    if not errors:
        return None
    if len(errors) == 1:
        return errors[0]
    return '\n- '.join(('Multiple errors:',) + errors)
