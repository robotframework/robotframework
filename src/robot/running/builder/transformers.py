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

from robot.errors import DataError
from robot.output import LOGGER
from robot.parsing import File, Token
from robot.variables import VariableIterator

from .settings import FileSettings
from ..model import ResourceFile, TestSuite


class SettingsBuilder(NodeVisitor):

    def __init__(self, suite: TestSuite, settings: FileSettings):
        self.suite = suite
        self.settings = settings

    def visit_Documentation(self, node):
        self.suite.doc = node.value

    def visit_Metadata(self, node):
        self.suite.metadata[node.name] = node.value

    def visit_SuiteName(self, node):
        self.suite.name = node.value

    def visit_SuiteSetup(self, node):
        self.suite.setup.config(name=node.name, args=node.args,
                                lineno=node.lineno)

    def visit_SuiteTeardown(self, node):
        self.suite.teardown.config(name=node.name, args=node.args,
                                   lineno=node.lineno)

    def visit_TestSetup(self, node):
        self.settings.test_setup = {'name': node.name, 'args': node.args,
                                    'lineno': node.lineno}

    def visit_TestTeardown(self, node):
        self.settings.test_teardown = {'name': node.name, 'args': node.args,
                                       'lineno': node.lineno}

    def visit_TestTimeout(self, node):
        self.settings.test_timeout = node.value

    def visit_DefaultTags(self, node):
        self.settings.default_tags = node.values

    def visit_ForceTags(self, node):
        self.settings.test_tags = node.values

    def visit_KeywordTags(self, node):
        self.settings.keyword_tags = node.values

    def visit_TestTemplate(self, node):
        self.settings.test_template = node.value

    def visit_LibraryImport(self, node):
        self.suite.resource.imports.library(node.name, node.args, node.alias, node.lineno)

    def visit_ResourceImport(self, node):
        self.suite.resource.imports.resource(node.name, node.lineno)

    def visit_VariablesImport(self, node):
        self.suite.resource.imports.variables(node.name, node.args, node.lineno)

    def visit_VariableSection(self, node):
        pass

    def visit_TestCaseSection(self, node):
        pass

    def visit_KeywordSection(self, node):
        pass


class SuiteBuilder(NodeVisitor):

    def __init__(self, suite: TestSuite, settings: FileSettings):
        self.suite = suite
        self.settings = settings
        self.rpa = None

    def build(self, model: File):
        ErrorReporter(model.source).visit(model)
        SettingsBuilder(self.suite, self.settings).visit(model)
        self.visit(model)
        if self.rpa is not None:
            self.suite.rpa = self.rpa

    def visit_SettingSection(self, node):
        pass

    def visit_Variable(self, node):
        self.suite.resource.variables.create(name=node.name,
                                             value=node.value,
                                             lineno=node.lineno,
                                             error=format_error(node.errors))

    def visit_TestCaseSection(self, node):
        if self.rpa is None:
            self.rpa = node.tasks
        elif self.rpa != node.tasks:
            raise DataError('One file cannot have both tests and tasks.')
        self.generic_visit(node)

    def visit_TestCase(self, node):
        TestCaseBuilder(self.suite, self.settings).visit(node)

    def visit_Keyword(self, node):
        KeywordBuilder(self.suite.resource, self.settings).visit(node)


class ResourceBuilder(NodeVisitor):

    def __init__(self, resource: ResourceFile):
        self.resource = resource
        self.settings = FileSettings()

    def build(self, model: File):
        ErrorReporter(model.source, raise_on_invalid_header=True).visit(model)
        self.visit(model)

    def visit_Documentation(self, node):
        self.resource.doc = node.value

    def visit_KeywordTags(self, node):
        self.settings.keyword_tags = node.values

    def visit_LibraryImport(self, node):
        self.resource.imports.library(node.name, node.args, node.alias, node.lineno)

    def visit_ResourceImport(self, node):
        self.resource.imports.resource(node.name, node.lineno)

    def visit_VariablesImport(self, node):
        self.resource.imports.variables(node.name, node.args, node.lineno)

    def visit_Variable(self, node):
        self.resource.variables.create(name=node.name,
                                       value=node.value,
                                       lineno=node.lineno,
                                       error=format_error(node.errors))

    def visit_Keyword(self, node):
        KeywordBuilder(self.resource, self.settings).visit(node)


class TestCaseBuilder(NodeVisitor):

    def __init__(self, suite: TestSuite, settings: FileSettings):
        self.suite = suite
        self.settings = settings
        self.test = None
        self.tags = None

    def visit_TestCase(self, node):
        error = format_error(node.errors + node.header.errors)
        settings = self.settings
        self.test = self.suite.tests.create(name=node.name,
                                            lineno=node.lineno,
                                            tags=settings.test_tags,
                                            timeout=settings.test_timeout,
                                            template=settings.test_template,
                                            error=error)
        if settings.test_setup:
            self.test.setup.config(**settings.test_setup)
        if settings.test_teardown:
            self.test.teardown.config(**settings.test_teardown)
        self.generic_visit(node)
        tags = self.tags if self.tags is not None else settings.default_tags
        if tags:
            self.test.tags.add(tags)
        if self.test.template:
            self._set_template(self.test, self.test.template)

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

    def visit_While(self, node):
        WhileBuilder(self.test).build(node)

    def visit_If(self, node):
        IfBuilder(self.test).build(node)

    def visit_Try(self, node):
        TryBuilder(self.test).build(node)

    def visit_TemplateArguments(self, node):
        self.test.body.create_keyword(args=node.args, lineno=node.lineno)

    def visit_Documentation(self, node):
        self.test.doc = node.value

    def visit_Setup(self, node):
        self.test.setup.config(name=node.name, args=node.args, lineno=node.lineno)

    def visit_Teardown(self, node):
        self.test.teardown.config(name=node.name, args=node.args, lineno=node.lineno)

    def visit_Timeout(self, node):
        self.test.timeout = node.value

    def visit_Tags(self, node):
        deprecate_tags_starting_with_hyphen(node, self.suite.source)
        self.tags = node.values

    def visit_Template(self, node):
        self.test.template = node.value

    def visit_KeywordCall(self, node):
        self.test.body.create_keyword(name=node.keyword, args=node.args,
                                      assign=node.assign, lineno=node.lineno)

    def visit_ReturnStatement(self, node):
        self.test.body.create_return(node.values, lineno=node.lineno,
                                     error=format_error(node.errors))

    def visit_Continue(self, node):
        self.test.body.create_continue(lineno=node.lineno,
                                       error=format_error(node.errors))

    def visit_Break(self, node):
        self.test.body.create_break(lineno=node.lineno,
                                    error=format_error(node.errors))

    def visit_Error(self, node):
        self.test.body.create_error(lineno=node.lineno,
                                    values=node.values, error=format_error(node.errors))


class KeywordBuilder(NodeVisitor):

    def __init__(self, resource: ResourceFile, settings: FileSettings):
        self.resource = resource
        self.settings = settings
        self.kw = None

    def visit_Keyword(self, node):
        error = format_error(node.errors + node.header.errors)
        self.kw = self.resource.keywords.create(name=node.name,
                                                tags=self.settings.keyword_tags,
                                                lineno=node.lineno,
                                                error=error)
        self.generic_visit(node)

    def visit_Documentation(self, node):
        self.kw.doc = node.value

    def visit_Arguments(self, node):
        self.kw.args = node.values
        if node.errors:
            error = format_error(node.errors)
            self.kw.error = f'Invalid argument specification: {error}'

    def visit_Tags(self, node):
        deprecate_tags_starting_with_hyphen(node, self.resource.source)
        self.kw.tags.add(node.values)

    def visit_Return(self, node):
        self.kw.return_ = node.values

    def visit_Timeout(self, node):
        self.kw.timeout = node.value

    def visit_Teardown(self, node):
        self.kw.teardown.config(name=node.name, args=node.args,
                                lineno=node.lineno)

    def visit_KeywordCall(self, node):
        self.kw.body.create_keyword(name=node.keyword, args=node.args,
                                    assign=node.assign, lineno=node.lineno)

    def visit_ReturnStatement(self, node):
        self.kw.body.create_return(node.values, lineno=node.lineno,
                                   error=format_error(node.errors))

    def visit_Continue(self, node):
        self.kw.body.create_continue(lineno=node.lineno,
                                     error=format_error(node.errors))

    def visit_Break(self, node):
        self.kw.body.create_break(lineno=node.lineno,
                                  error=format_error(node.errors))

    def visit_For(self, node):
        ForBuilder(self.kw).build(node)

    def visit_While(self, node):
        WhileBuilder(self.kw).build(node)

    def visit_If(self, node):
        IfBuilder(self.kw).build(node)

    def visit_Try(self, node):
        TryBuilder(self.kw).build(node)

    def visit_Error(self, node):
        self.kw.body.create_error(lineno=node.lineno,
                                  values=node.values, error=format_error(node.errors))


class ForBuilder(NodeVisitor):

    def __init__(self, parent):
        self.parent = parent
        self.model = None

    def build(self, node):
        error = format_error(self._get_errors(node))
        self.model = self.parent.body.create_for(
            node.variables, node.flavor, node.values, node.start, node.mode, node.fill,
            lineno=node.lineno, error=error
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

    def visit_While(self, node):
        WhileBuilder(self.model).build(node)

    def visit_If(self, node):
        IfBuilder(self.model).build(node)

    def visit_Try(self, node):
        TryBuilder(self.model).build(node)

    def visit_ReturnStatement(self, node):
        self.model.body.create_return(node.values, lineno=node.lineno,
                                      error=format_error(node.errors))

    def visit_Continue(self, node):
        self.model.body.create_continue(lineno=node.lineno,
                                        error=format_error(node.errors))

    def visit_Break(self, node):
        self.model.body.create_break(lineno=node.lineno,
                                     error=format_error(node.errors))

    def visit_Error(self, node):
        self.model.body.create_error(lineno=node.lineno,
                                    values=node.values, error=format_error(node.errors))


class IfBuilder(NodeVisitor):

    def __init__(self, parent):
        self.parent = parent
        self.model = None

    def build(self, node):
        root = self.parent.body.create_if(lineno=node.lineno,
                                          error=format_error(self._get_errors(node)))
        assign = node.assign
        node_type = None
        while node:
            node_type = node.type if node.type != 'INLINE IF' else 'IF'
            self.model = root.body.create_branch(node_type, node.condition,
                                                 lineno=node.lineno)
            for step in node.body:
                self.visit(step)
            if assign:
                for item in self.model.body:
                    # Having assign when model item doesn't support assign is an error,
                    # but it has been handled already when model was validated.
                    if hasattr(item, 'assign'):
                        item.assign = assign
            node = node.orelse
        # Smallish hack to make sure assignment is always run.
        if assign and node_type != 'ELSE':
            root.body.create_branch('ELSE').body.create_keyword(
                assign=assign, name='BuiltIn.Set Variable', args=['${NONE}']
            )
        return root

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

    def visit_For(self, node):
        ForBuilder(self.model).build(node)

    def visit_While(self, node):
        WhileBuilder(self.model).build(node)

    def visit_If(self, node):
        IfBuilder(self.model).build(node)

    def visit_Try(self, node):
        TryBuilder(self.model).build(node)

    def visit_ReturnStatement(self, node):
        self.model.body.create_return(node.values, lineno=node.lineno,
                                      error=format_error(node.errors))

    def visit_Continue(self, node):
        self.model.body.create_continue(lineno=node.lineno,
                                        error=format_error(node.errors))

    def visit_Break(self, node):
        self.model.body.create_break(lineno=node.lineno,
                                     error=format_error(node.errors))

    def visit_Error(self, node):
        self.model.body.create_error(lineno=node.lineno,
                                     values=node.values, error=format_error(node.errors))


class TryBuilder(NodeVisitor):

    def __init__(self, parent):
        self.parent = parent
        self.model = None
        self.template_error = None

    def build(self, node):
        root = self.parent.body.create_try(lineno=node.lineno)
        errors = self._get_errors(node)
        while node:
            self.model = root.body.create_branch(node.type, node.patterns,
                                                 node.pattern_type, node.variable,
                                                 lineno=node.lineno)
            for step in node.body:
                self.visit(step)
            node = node.next
        if self.template_error:
            errors += (self.template_error,)
        if errors:
            root.error = format_error(errors)
        return root

    def _get_errors(self, node):
        errors = node.header.errors + node.errors
        if node.next:
            errors += self._get_errors(node.next)
        if node.end:
            errors += node.end.errors
        return errors

    def visit_For(self, node):
        ForBuilder(self.model).build(node)

    def visit_While(self, node):
        WhileBuilder(self.model).build(node)

    def visit_If(self, node):
        IfBuilder(self.model).build(node)

    def visit_Try(self, node):
        TryBuilder(self.model).build(node)

    def visit_ReturnStatement(self, node):
        self.model.body.create_return(node.values, lineno=node.lineno,
                                      error=format_error(node.errors))

    def visit_Continue(self, node):
        self.model.body.create_continue(lineno=node.lineno,
                                        error=format_error(node.errors))

    def visit_Break(self, node):
        self.model.body.create_break(lineno=node.lineno,
                                     error=format_error(node.errors))

    def visit_KeywordCall(self, node):
        self.model.body.create_keyword(name=node.keyword, args=node.args,
                                       assign=node.assign, lineno=node.lineno)

    def visit_TemplateArguments(self, node):
        self.template_error = 'Templates cannot be used with TRY.'

    def visit_Error(self, node):
        self.model.body.create_error(lineno=node.lineno,
                                     values=node.values, error=format_error(node.errors))


class WhileBuilder(NodeVisitor):

    def __init__(self, parent):
        self.parent = parent
        self.model = None

    def build(self, node):
        error = format_error(self._get_errors(node))
        self.model = self.parent.body.create_while(
            node.condition, node.limit, node.on_limit,
            node.on_limit_message, lineno=node.lineno, error=error
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

    def visit_While(self, node):
        WhileBuilder(self.model).build(node)

    def visit_If(self, node):
        IfBuilder(self.model).build(node)

    def visit_Try(self, node):
        TryBuilder(self.model).build(node)

    def visit_ReturnStatement(self, node):
        self.model.body.create_return(node.values, lineno=node.lineno,
                                      error=format_error(node.errors))

    def visit_Break(self, node):
        self.model.body.create_break(error=format_error(node.errors))

    def visit_Continue(self, node):
        self.model.body.create_continue(error=format_error(node.errors))

    def visit_Error(self, node):
        self.model.body.create_error(lineno=node.lineno,
                                     values=node.values, error=format_error(node.errors))


def format_error(errors):
    if not errors:
        return None
    if len(errors) == 1:
        return errors[0]
    return '\n- '.join(('Multiple errors:',) + errors)


def deprecate_tags_starting_with_hyphen(node, source):
    for tag in node.values:
        if tag.startswith('-'):
            LOGGER.warn(
                f"Error in file '{source}' on line {node.lineno}: "
                f"Settings tags starting with a hyphen using the '[Tags]' setting "
                f"is deprecated. In Robot Framework 7.0 this syntax will be used "
                f"for removing tags. Escape '{tag}' like '\\{tag}' to use the "
                f"literal value and to avoid this warning."
            )


class ErrorReporter(NodeVisitor):

    def __init__(self, source, raise_on_invalid_header=False):
        self.source = source
        self.raise_on_invalid_header = raise_on_invalid_header

    def visit_TestCase(self, node):
        pass

    def visit_Keyword(self, node):
        pass

    def visit_SectionHeader(self, node):
        token = node.get_token(Token.INVALID_HEADER)
        if token:
            if self.raise_on_invalid_header:
                raise DataError(self._format_message(token))
            else:
                LOGGER.error(self._format_message(token))

    def visit_Error(self, node):
        for error in node.get_tokens(Token.ERROR):
            LOGGER.error(self._format_message(error))

    def _format_message(self, token):
        return f"Error in file '{self.source}' on line {token.lineno}: {token.error}"
