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
from robot.variables import VariableMatches

from .settings import FileSettings
from ..model import (For, If, IfBranch, ResourceFile, TestSuite, TestCase, Try,
                     TryBranch, UserKeyword, While)


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

    def visit_TestTags(self, node):
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
                                             separator=node.separator,
                                             lineno=node.lineno,
                                             error=format_error(node.errors))

    def visit_TestCaseSection(self, node):
        if self.rpa is None:
            self.rpa = node.tasks
        elif self.rpa != node.tasks:
            raise DataError('One file cannot have both tests and tasks.')
        self.generic_visit(node)

    def visit_TestCase(self, node):
        TestCaseBuilder(self.suite, self.settings).build(node)

    def visit_Keyword(self, node):
        KeywordBuilder(self.suite.resource, self.settings).build(node)


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
                                       separator=node.separator,
                                       lineno=node.lineno,
                                       error=format_error(node.errors))

    def visit_Keyword(self, node):
        KeywordBuilder(self.resource, self.settings).build(node)


class BodyBuilder(NodeVisitor):

    def __init__(self, model: 'TestCase|UserKeyword|For|If|Try|While|None' = None):
        self.model = model

    def visit_For(self, node):
        ForBuilder(self.model).build(node)

    def visit_While(self, node):
        WhileBuilder(self.model).build(node)

    def visit_If(self, node):
        IfBuilder(self.model).build(node)

    def visit_Try(self, node):
        TryBuilder(self.model).build(node)

    def visit_KeywordCall(self, node):
        self.model.body.create_keyword(name=node.keyword, args=node.args,
                                       assign=node.assign, lineno=node.lineno)

    def visit_TemplateArguments(self, node):
        self.model.body.create_keyword(args=node.args, lineno=node.lineno)

    def visit_Var(self, node):
        self.model.body.create_var(node.name, node.value, node.scope, node.separator,
                                   lineno=node.lineno, error=format_error(node.errors))

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


class TestCaseBuilder(BodyBuilder):
    model: TestCase

    def __init__(self, suite: TestSuite, settings: FileSettings):
        super().__init__(suite.tests.create())
        self.settings = settings
        self._test_has_tags = False

    def build(self, node):
        settings = self.settings
        # Possible parsing errors aren't reported further with tests because:
        # - We only validate that test body or name isn't empty.
        # - That is validated again during execution.
        # - This way e.g. model modifiers can add content to body.
        self.model.config(name=node.name, tags=settings.test_tags,
                          timeout=settings.test_timeout,
                          template=settings.test_template,
                          lineno=node.lineno)
        if settings.test_setup:
            self.model.setup.config(**settings.test_setup)
        if settings.test_teardown:
            self.model.teardown.config(**settings.test_teardown)
        self.generic_visit(node)
        if not self._test_has_tags:
            self.model.tags.add(settings.default_tags)
        if self.model.template:
            self._set_template(self.model, self.model.template)

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
        matches = VariableMatches(template, identifiers='$')
        count = len(matches)
        if count == 0 or count != len(arguments):
            return template, arguments
        temp = []
        for match, arg in zip(matches, arguments):
            temp[-1:] = [match.before, arg, match.after]
        return ''.join(temp), ()

    def visit_Documentation(self, node):
        self.model.doc = node.value

    def visit_Setup(self, node):
        self.model.setup.config(name=node.name, args=node.args, lineno=node.lineno)

    def visit_Teardown(self, node):
        self.model.teardown.config(name=node.name, args=node.args, lineno=node.lineno)

    def visit_Timeout(self, node):
        self.model.timeout = node.value

    def visit_Tags(self, node):
        for tag in node.values:
            if tag.startswith('-'):
                self.model.tags.remove(tag[1:])
            else:
                self.model.tags.add(tag)
        self._test_has_tags = True

    def visit_Template(self, node):
        self.model.template = node.value


class KeywordBuilder(BodyBuilder):
    model: UserKeyword

    def __init__(self, resource: ResourceFile, settings: FileSettings):
        super().__init__(resource.keywords.create(tags=settings.keyword_tags))

    def build(self, node):
        # Possible parsing errors aren't reported further because:
        # - We only validate that keyword body or name isn't empty.
        # - That is validated again during execution.
        # - This way e.g. model modifiers can add content to body.
        self.model.config(name=node.name, lineno=node.lineno)
        self.generic_visit(node)

    def visit_Documentation(self, node):
        self.model.doc = node.value

    def visit_Arguments(self, node):
        self.model.args = node.values
        if node.errors:
            error = format_error(node.errors)
            self.model.error = f'Invalid argument specification: {error}'

    def visit_Tags(self, node):
        for tag in node.values:
            if tag.startswith('-'):
                self.model.tags.remove(tag[1:])
            else:
                self.model.tags.add(tag)

    def visit_Return(self, node):
        ErrorReporter(self.model.source).visit(node)
        self.model.return_ = node.values

    def visit_Timeout(self, node):
        self.model.timeout = node.value

    def visit_Setup(self, node):
        self.model.setup.config(name=node.name, args=node.args, lineno=node.lineno)

    def visit_Teardown(self, node):
        self.model.teardown.config(name=node.name, args=node.args, lineno=node.lineno)

    def visit_KeywordCall(self, node):
        self.model.body.create_keyword(name=node.keyword, args=node.args,
                                       assign=node.assign, lineno=node.lineno)


class ForBuilder(BodyBuilder):
    model: For

    def __init__(self, parent: 'TestCase|UserKeyword|For|If|Try|While'):
        super().__init__(parent.body.create_for())

    def build(self, node):
        error = format_error(self._get_errors(node))
        self.model.config(assign=node.assign, flavor=node.flavor, values=node.values,
                          start=node.start, mode=node.mode, fill=node.fill,
                          lineno=node.lineno, error=error)
        for step in node.body:
            self.visit(step)
        return self.model

    def _get_errors(self, node):
        errors = node.header.errors + node.errors
        if node.end:
            errors += node.end.errors
        return errors


class IfBuilder(BodyBuilder):
    model: 'IfBranch|None'

    def __init__(self, parent: 'TestCase|UserKeyword|For|If|Try|While'):
        super().__init__()
        self.root = parent.body.create_if()

    def build(self, node):
        self.root.config(lineno=node.lineno, error=format_error(self._get_errors(node)))
        assign = node.assign
        node_type = None
        while node:
            node_type = node.type if node.type != 'INLINE IF' else 'IF'
            self.model = self.root.body.create_branch(node_type, node.condition,
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
            self.root.body.create_branch('ELSE').body.create_keyword(
                assign=assign, name='BuiltIn.Set Variable', args=['${NONE}']
            )
        return self.root

    def _get_errors(self, node):
        errors = node.header.errors + node.errors
        if node.orelse:
            errors += self._get_errors(node.orelse)
        if node.end:
            errors += node.end.errors
        return errors


class TryBuilder(BodyBuilder):
    model: 'TryBranch|None'

    def __init__(self, parent: 'TestCase|UserKeyword|For|If|Try|While'):
        super().__init__()
        self.root = parent.body.create_try()
        self.template_error = None

    def build(self, node):
        self.root.config(lineno=node.lineno)
        errors = self._get_errors(node)
        while node:
            self.model = self.root.body.create_branch(node.type, node.patterns,
                                                      node.pattern_type, node.assign,
                                                      lineno=node.lineno)
            for step in node.body:
                self.visit(step)
            node = node.next
        if self.template_error:
            errors += (self.template_error,)
        if errors:
            self.root.error = format_error(errors)
        return self.root

    def _get_errors(self, node):
        errors = node.header.errors + node.errors
        if node.next:
            errors += self._get_errors(node.next)
        if node.end:
            errors += node.end.errors
        return errors

    def visit_TemplateArguments(self, node):
        self.template_error = 'Templates cannot be used with TRY.'


class WhileBuilder(BodyBuilder):
    model: While

    def __init__(self, parent: 'TestCase|UserKeyword|For|If|Try|While'):
        super().__init__(parent.body.create_while())

    def build(self, node):
        error = format_error(self._get_errors(node))
        self.model.config(condition=node.condition, limit=node.limit,
                          on_limit=node.on_limit, on_limit_message=node.on_limit_message,
                          lineno=node.lineno, error=error)
        for step in node.body:
            self.visit(step)
        return self.model

    def _get_errors(self, node):
        errors = node.header.errors + node.errors
        if node.end:
            errors += node.end.errors
        return errors


def format_error(errors):
    if not errors:
        return None
    if len(errors) == 1:
        return errors[0]
    return '\n- '.join(('Multiple errors:',) + errors)


class ErrorReporter(NodeVisitor):

    def __init__(self, source, raise_on_invalid_header=False):
        self.source = source
        self.raise_on_invalid_header = raise_on_invalid_header

    def visit_TestCase(self, node):
        pass

    def visit_Keyword(self, node):
        pass

    def visit_Return(self, node):
        # Empty 'visit_Keyword' above prevents calling this when visiting the whole
        # model, but 'KeywordBuilder.visit_Return' visits the node it gets.
        LOGGER.warn(self._format_message(node.get_token(Token.RETURN_SETTING)))

    def visit_SectionHeader(self, node):
        token = node.get_token(*Token.HEADER_TOKENS)
        if not token.error:
            return
        message = self._format_message(token)
        if token.type == Token.INVALID_HEADER:
            if self.raise_on_invalid_header:
                raise DataError(message)
            else:
                LOGGER.error(message)
        else:
            # Errors, other than totally invalid headers, can occur only with
            # deprecated singular headers, and we want to report them as warnings.
            # A more generic solution for separating errors and warnings would be good.
            LOGGER.warn(self._format_message(token))

    def visit_Error(self, node):
        for error in node.get_tokens(Token.ERROR):
            LOGGER.error(self._format_message(error))

    def _format_message(self, token):
        return f"Error in file '{self.source}' on line {token.lineno}: {token.error}"
