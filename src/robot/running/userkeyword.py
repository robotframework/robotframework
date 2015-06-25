#  Copyright 2008-2015 Nokia Solutions and Networks
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

from robot.errors import (DataError, ExecutionFailed, ExecutionPassed,
                          PassExecution, ReturnFromKeyword,
                          UserKeywordExecutionFailed)
from robot.variables import is_list_var
from robot.output import LOGGER
from robot import utils

from .arguments import (ArgumentMapper, ArgumentResolver,
                        EmbeddedArguments, UserKeywordArgumentParser)
from .handlerstore import HandlerStore
from .keywordrunner import KeywordRunner
from .timeouts import KeywordTimeout
from .usererrorhandler import UserErrorHandler


class UserLibrary(object):

    def __init__(self, user_keywords, path=None):
        basename = os.path.basename(path) if path else None
        self.name = os.path.splitext(basename)[0] if path else None
        self.handlers = HandlerStore(basename)
        for kw in user_keywords:
            try:
                handler, embedded = self._create_handler(kw)
                self._validate_not_duplicate(handler)
            except DataError as err:
                LOGGER.error("Creating user keyword '%s' failed: %s"
                             % (kw.name, unicode(err)))
                handler = UserErrorHandler(kw.name, unicode(err))
                embedded = False
            self.handlers.add(handler, embedded)

    def _create_handler(self, kw):
        embedded = EmbeddedArguments(kw.name)
        if embedded:
            if kw.args:
                raise DataError('Keyword cannot have both normal and embedded '
                                'arguments.')
            return EmbeddedArgsTemplate(kw, self.name, embedded), True
        return UserKeywordHandler(kw, self.name), False

    def _validate_not_duplicate(self, handler):
        if handler.name in self.handlers:
            self.handlers.remove(handler.name)
            raise DataError('Keyword with same name defined multiple times.')


class UserKeywordHandler(object):
    type = 'user'

    def __init__(self, keyword, libname):
        self.name = keyword.name
        self.keywords = keyword.keywords.normal
        self.return_value = tuple(keyword.return_)
        self.teardown = keyword.keywords.teardown
        self.libname = libname
        self.doc = self._doc = unicode(keyword.doc)
        self.tags = self._tags = keyword.tags
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
        # TODO: Should use runner and not change internal state like this.
        # Timeouts should also be cleaned up in general.
        doc = variables.replace_string(self._doc, ignore_errors=True)
        doc, tags = utils.split_tags_from_doc(doc)
        self.doc = doc
        self.tags = [variables.replace_string(tag, ignore_errors=True)
                     for tag in self._tags] + tags
        if self._timeout:
            self.timeout = KeywordTimeout(self._timeout.value,
                                          self._timeout.message,
                                          variables)
        else:
            self.timeout = KeywordTimeout()

    def run(self, context, arguments):
        arguments = self._resolve_arguments(context, arguments)
        with context.user_keyword(self):
            args, kwargs = self._map_arguments(context, arguments)
            if context.dry_run:
                return self._dry_run(context, args, kwargs)
            return self._normal_run(context, args, kwargs)

    def _resolve_arguments(self, context, arguments):
        variables = context.variables if not context.dry_run else None
        resolver = ArgumentResolver(self.arguments)
        return resolver.resolve(arguments, variables)

    def _map_arguments(self, context, arguments):
        positional, named = arguments
        variables = context.variables if not context.dry_run else None
        mapper = ArgumentMapper(self.arguments)
        return mapper.map(positional, named, variables)

    def _dry_run(self, context, args, kwargs):
        error, return_ = self._execute(context, args, kwargs)
        if error:
            raise error
        return None

    def _normal_run(self, context, args, kwargs):
        error, return_ = self._execute(context, args, kwargs)
        if error and not error.can_continue(context.in_teardown):
            raise error
        return_value = self._get_return_value(context.variables, return_)
        if error:
            error.return_value = return_value
            raise error
        return return_value

    def _execute(self, context, positional, kwargs):
        self._set_variables(positional, kwargs, context.variables)
        context.output.trace(lambda: self._log_args(context.variables))
        self._verify_keyword_is_valid()
        self.timeout.start()
        error = return_ = pass_ = None
        runner = KeywordRunner(context)
        try:
            runner.run_keywords(self.keywords)
        except ReturnFromKeyword as exception:
            return_ = exception
            error = exception.earlier_failures
        except ExecutionPassed as exception:
            pass_ = exception
            error = exception.earlier_failures
        except ExecutionFailed as exception:
            error = exception
        with context.keyword_teardown(error):
            td_error = self._run_teardown(context)
        if error or td_error:
            error = UserKeywordExecutionFailed(error, td_error)
        return error or pass_, return_

    def _set_variables(self, positional, kwargs, variables):
        before_varargs, varargs = self._split_args_and_varargs(positional)
        for name, value in zip(self.arguments.positional, before_varargs):
            variables['${%s}' % name] = value
        if self.arguments.varargs:
            variables['@{%s}' % self.arguments.varargs] = varargs
        if self.arguments.kwargs:
            variables['&{%s}' % self.arguments.kwargs] = kwargs

    def _split_args_and_varargs(self, args):
        if not self.arguments.varargs:
            return args, []
        positional = len(self.arguments.positional)
        return args[:positional], args[positional:]

    def _log_args(self, variables):
        args = ['${%s}' % arg for arg in self.arguments.positional]
        if self.arguments.varargs:
            args.append('@{%s}' % self.arguments.varargs)
        if self.arguments.kwargs:
            args.append('&{%s}' % self.arguments.kwargs)
        args = ['%s=%s' % (name, utils.prepr(variables[name]))
                for name in args]
        return 'Arguments: [ %s ]' % ' | '.join(args)

    def _run_teardown(self, context):
        if not self.teardown:
            return None
        try:
            name = context.variables.replace_string(self.teardown.name)
        except DataError as err:
            return ExecutionFailed(unicode(err), syntax=True)
        if name.upper() in ('', 'NONE'):
            return None
        runner = KeywordRunner(context)
        try:
            runner.run_keyword(self.teardown, name)
        except PassExecution:
            return None
        except ExecutionFailed as err:
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
        except DataError as err:
            raise DataError('Replacing variables from keyword return value '
                            'failed: %s' % unicode(err))
        if len(ret) != 1 or contains_list_var:
            return ret
        return ret[0]


class EmbeddedArgsTemplate(UserKeywordHandler):

    def __init__(self, keyword, libname, embedded):
        UserKeywordHandler.__init__(self, keyword, libname)
        self.keyword = keyword
        self.embedded_name = embedded.name
        self.embedded_args = embedded.args

    def matches(self, name):
        return self.embedded_name.match(name) is not None

    def create(self, name):
        return EmbeddedArgs(name, self)


class EmbeddedArgs(UserKeywordHandler):

    def __init__(self, name, template):
        match = template.embedded_name.match(name)
        if not match:
            raise ValueError('Does not match given name')
        UserKeywordHandler.__init__(self, template.keyword, template.libname)
        self.embedded_args = zip(template.embedded_args, match.groups())
        self.name = name
        self.orig_name = template.name

    def _resolve_arguments(self, context, arguments):
        variables = context.variables if not context.dry_run else None
        # Validates that no arguments given.
        ArgumentResolver(self.arguments).resolve(arguments, variables)
        if not variables:
            return self.embedded_args
        return [(n, variables.replace_scalar(v)) for n, v in self.embedded_args]

    def _map_arguments(self, context, arguments):
        if not context.dry_run:
            for name, value in arguments:
                context.variables['${%s}' % name] = value
        return [], {}
