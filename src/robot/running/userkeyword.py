#  Copyright 2008-2014 Nokia Solutions and Networks
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

from __future__ import with_statement

import os
import re

from robot.errors import (DataError, ExecutionFailed, ExecutionPassed,
                          PassExecution, ReturnFromKeyword,
                          UserKeywordExecutionFailed)
from robot.variables import is_list_var, VariableIterator
from robot.output import LOGGER
from robot import utils

from .arguments import (ArgumentMapper, ArgumentResolver,
                        UserKeywordArgumentParser)
from .baselibrary import BaseLibrary
from .keywords import Keywords, Keyword
from .timeouts import KeywordTimeout
from .usererrorhandler import UserErrorHandler


class UserLibrary(BaseLibrary):

    def __init__(self, user_keywords, path=None):
        self.name = self._get_name_for_resource_file(path)
        self.handlers = utils.NormalizedDict(ignore=['_'])
        self.embedded_arg_handlers = []
        for kw in user_keywords:
            try:
                handler = self._create_handler(kw)
            except DataError, err:
                LOGGER.error("Creating user keyword '%s' failed: %s"
                             % (kw.name, unicode(err)))
                continue
            if handler.name in self.handlers:
                error = "Keyword '%s' defined multiple times." % handler.name
                handler = UserErrorHandler(handler.name, error)
            self.handlers[handler.name] = handler

    def _create_handler(self, kw):
        try:
            handler = EmbeddedArgsTemplate(kw, self.name)
        except TypeError:
            handler = UserKeywordHandler(kw, self.name)
        else:
            self.embedded_arg_handlers.append(handler)
        return handler

    def _get_name_for_resource_file(self, path):
        if path is None:
            return None
        return os.path.splitext(os.path.basename(path))[0]

    def has_handler(self, name):
        if BaseLibrary.has_handler(self, name):
            return True
        for template in self.embedded_arg_handlers:
            try:
                EmbeddedArgs(name, template)
            except TypeError:
                pass
            else:
                return True
        return False

    def get_handler(self, name):
        try:
            return BaseLibrary.get_handler(self, name)
        except DataError, error:
            found = self._get_embedded_arg_handlers(name)
            if not found:
                raise error
            if len(found) == 1:
                return found[0]
            self._raise_multiple_matching_keywords_found(name, found)

    def _get_embedded_arg_handlers(self, name):
        found = []
        for template in self.embedded_arg_handlers:
            try:
                found.append(EmbeddedArgs(name, template))
            except TypeError:
                pass
        return found

    def _raise_multiple_matching_keywords_found(self, name, found):
        names = utils.seq2str([f.orig_name for f in found])
        if self.name is None:
            where = "Test case file"
        else:
            where = "Resource file '%s'" % self.name
        raise DataError("%s contains multiple keywords matching name '%s'\n"
                        "Found: %s" % (where, name, names))


class UserKeywordHandler(object):
    type = 'user'

    def __init__(self, keyword, libname):
        self.name = keyword.name
        self.keywords = Keywords(keyword.steps)
        self.return_value = tuple(keyword.return_)
        self.teardown = keyword.teardown
        self.libname = libname
        self.doc = self._doc = unicode(keyword.doc)
        self.arguments = UserKeywordArgumentParser().parse(tuple(keyword.args),
                                                           self.longname)
        self._timeout = keyword.timeout

    @property
    def longname(self):
        return '%s.%s' % (self.libname, self.name) if self.libname else self.name

    @property
    def shortdoc(self):
        return self.doc.splitlines()[0] if self.doc else ''

    def init_keyword(self, variables):
        self.doc = variables.replace_string(self._doc, ignore_errors=True)
        timeout = (self._timeout.value, self._timeout.message) if self._timeout else ()
        self.timeout = KeywordTimeout(*timeout)
        self.timeout.replace_variables(variables)

    def run(self, context, arguments):
        context.start_user_keyword(self)
        try:
            return self._run(context, arguments)
        finally:
            context.end_user_keyword()

    def _run(self, context, arguments):
        if context.dry_run:
            return self._dry_run(context, arguments)
        return self._normal_run(context, arguments)

    def _dry_run(self, context, arguments):
        arguments = self._resolve_arguments(arguments)
        error, return_ = self._execute(context, arguments)
        if error:
            raise error
        return None

    def _normal_run(self, context, arguments):
        arguments = self._resolve_arguments(arguments, context.variables)
        error, return_ = self._execute(context, arguments)
        if error and not error.can_continue(context.in_teardown):
            raise error
        return_value = self._get_return_value(context.variables, return_)
        if error:
            error.return_value = return_value
            raise error
        return return_value

    def _resolve_arguments(self, arguments, variables=None):
        resolver = ArgumentResolver(self.arguments)
        mapper = ArgumentMapper(self.arguments)
        positional, named = resolver.resolve(arguments, variables)
        arguments, _ = mapper.map(positional, named, variables)
        return arguments

    def _execute(self, context, arguments):
        self._set_variables(arguments, context.variables)
        context.output.trace(lambda: self._log_args(context.variables))
        self._verify_keyword_is_valid()
        self.timeout.start()
        error = return_ = pass_ = None
        try:
            self.keywords.run(context)
        except ReturnFromKeyword, exception:
            return_ = exception
            error = exception.earlier_failures
        except ExecutionPassed, exception:
            pass_ = exception
            error = exception.earlier_failures
        except ExecutionFailed, exception:
            error = exception
        with context.keyword_teardown(error):
            td_error = self._run_teardown(context)
        if error or td_error:
            error = UserKeywordExecutionFailed(error, td_error)
        return error or pass_, return_

    def _set_variables(self, arguments, variables):
        before_varargs, varargs = self._split_args_and_varargs(arguments)
        for name, value in zip(self.arguments.positional, before_varargs):
            variables['${%s}' % name] = value
        if self.arguments.varargs:
            variables['@{%s}' % self.arguments.varargs] = varargs

    def _split_args_and_varargs(self, args):
        if not self.arguments.varargs:
            return args, []
        positional = len(self.arguments.positional)
        return args[:positional], args[positional:]

    def _log_args(self, variables):
        args = ['${%s}' % arg for arg in self.arguments.positional]
        if self.arguments.varargs:
            args.append('@{%s}' % self.arguments.varargs)
        args = ['%s=%s' % (name, utils.safe_repr(variables[name]))
                for name in args]
        return 'Arguments: [ %s ]' % ' | '.join(args)

    def _run_teardown(self, context):
        if not self.teardown:
            return None
        try:
            name = context.variables.replace_string(self.teardown.name)
        except DataError, err:
            return ExecutionFailed(unicode(err), syntax=True)
        if name.upper() in ('', 'NONE'):
            return None
        kw = Keyword(name, self.teardown.args, type='teardown')
        try:
            kw.run(context)
        except PassExecution:
            return None
        except ExecutionFailed, err:
            return err
        return None

    def _verify_keyword_is_valid(self):
        if not (self.keywords or self.return_value):
            raise DataError("User keyword '%s' contains no keywords."
                            % self.name)

    def _get_return_value(self, variables, return_):
        ret = self.return_value if not return_ else return_.return_value
        if not ret:
            return None
        contains_list_var = any(is_list_var(item) for item in ret)
        try:
            ret = variables.replace_list(ret)
        except DataError, err:
            raise DataError('Replacing variables from keyword return value '
                            'failed: %s' % unicode(err))
        if len(ret) != 1 or contains_list_var:
            return ret
        return ret[0]


class EmbeddedArgsTemplate(UserKeywordHandler):
    _regexp_extension = re.compile(r'(?<!\\)\(\?.+\)')
    _regexp_group_start = re.compile(r'(?<!\\)\((.*?)\)')
    _regexp_group_escape = r'(?:\1)'
    _default_pattern = '.*?'
    _variable_pattern = r'\$\{[^\}]+\}'

    def __init__(self, keyword, libname):
        if keyword.args:
            raise TypeError('Cannot have normal arguments')
        self.embedded_args, self.name_regexp \
                = self._read_embedded_args_and_regexp(keyword.name)
        if not self.embedded_args:
            raise TypeError('Must have embedded arguments')
        UserKeywordHandler.__init__(self, keyword, libname)
        self.keyword = keyword

    def _read_embedded_args_and_regexp(self, string):
        args = []
        full_pattern = ['^']
        for before, variable, string in VariableIterator(string, identifiers='$'):
            variable, pattern = self._get_regexp_pattern(variable[2:-1])
            args.append('${%s}' % variable)
            full_pattern.extend([re.escape(before), '(%s)' % pattern])
        full_pattern.extend([re.escape(string), '$'])
        return args, self._compile_regexp(full_pattern)

    def _get_regexp_pattern(self, variable):
        if ':' not in variable:
            return variable, self._default_pattern
        variable, pattern = variable.split(':', 1)
        return variable, self._format_custom_regexp(pattern)

    def _format_custom_regexp(self, pattern):
        for formatter in (self._regexp_extensions_are_not_allowed,
                          self._make_groups_non_capturing,
                          self._unescape_closing_curly,
                          self._add_automatic_variable_pattern):
            pattern = formatter(pattern)
        return pattern

    def _regexp_extensions_are_not_allowed(self, pattern):
        if not self._regexp_extension.search(pattern):
            return pattern
        raise DataError('Regexp extensions are not allowed in embedded '
                        'arguments.')

    def _make_groups_non_capturing(self, pattern):
        return self._regexp_group_start.sub(self._regexp_group_escape, pattern)

    def _unescape_closing_curly(self, pattern):
        return pattern.replace('\\}', '}')

    def _add_automatic_variable_pattern(self, pattern):
        return '%s|%s' % (pattern, self._variable_pattern)

    def _compile_regexp(self, pattern):
        try:
            return re.compile(''.join(pattern), re.IGNORECASE)
        except:
            raise DataError("Compiling embedded arguments regexp failed: %s"
                            % utils.get_error_message())


class EmbeddedArgs(UserKeywordHandler):

    def __init__(self, name, template):
        match = template.name_regexp.match(name)
        if not match:
            raise TypeError('Does not match given name')
        UserKeywordHandler.__init__(self, template.keyword, template.libname)
        self.embedded_args = zip(template.embedded_args, match.groups())
        self.name = name
        self.orig_name = template.name

    def _run(self, context, args):
        if not context.dry_run:
            variables = context.variables
            self._resolve_arguments(args, variables)  # validates no args given
            for name, value in self.embedded_args:
                variables[name] = variables.replace_scalar(value)
        return UserKeywordHandler._run(self, context, args)
