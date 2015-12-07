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

from robot.errors import DataError
from robot.output import LOGGER
from robot.utils import split_tags_from_doc, unic

from .arguments import (EmbeddedArguments, UserKeywordArgumentParser)
from .handlerstore import HandlerStore
from .userkeywordrunner import (UserKeywordRunner, UserKeywordDryRunner,
                                EmbeddedArgsUserKeywordRunner,
                                EmbeddedArgsUserKeywordDryRunner)
from .timeouts import KeywordTimeout
from .usererrorhandler import UserErrorHandler


class UserLibrary(object):
    TEST_CASE_FILE_TYPE = HandlerStore.TEST_CASE_FILE_TYPE
    RESOURCE_FILE_TYPE = HandlerStore.RESOURCE_FILE_TYPE

    def __init__(self, user_keywords, source, source_type=RESOURCE_FILE_TYPE):
        basename = os.path.basename(source) if source else None
        self.name = os.path.splitext(basename)[0] \
            if source_type == self.RESOURCE_FILE_TYPE else None
        self.handlers = HandlerStore(basename, source_type)
        self.source = source
        self.source_type = source_type
        for kw in user_keywords:
            try:
                handler = self._create_handler(kw)
            except DataError as error:
                handler = UserErrorHandler(kw.name, error, self.name)
                self._log_creating_failed(handler, error)
            embedded = isinstance(handler, EmbeddedArgsTemplate)
            try:
                self.handlers.add(handler, embedded)
            except DataError as error:
                self._log_creating_failed(handler, error)

    def _create_handler(self, kw):
        embedded = EmbeddedArguments(kw.name)
        if not embedded:
            return UserKeywordHandler(kw, self.name)
        if kw.args:
            raise DataError('Keyword cannot have both normal and embedded '
                            'arguments.')
        return EmbeddedArgsTemplate(kw, self.name, embedded)

    def _log_creating_failed(self, handler, error):
        LOGGER.error("Error in %s '%s': Creating keyword '%s' failed: %s"
                     % (self.source_type.lower(), self.source,
                        handler.name, error.message))


class UserKeywordHandler(object):
    type = 'user'

    def __init__(self, keyword, libname):
        self.name = keyword.name
        self.libname = libname
        self.doc = unic(keyword.doc)
        self.tags = keyword.tags
        self.arguments = UserKeywordArgumentParser().parse(tuple(keyword.args),
                                                           self.longname)
        self._kw = keyword

    @property
    def longname(self):
        return '%s.%s' % (self.libname, self.name) if self.libname else self.name

    @property
    def shortdoc(self):
        return self.doc.splitlines()[0] if self.doc else ''

    def create(self, name):
        return UserKeywordCall(self._kw, self.libname)


class UserKeywordCall(object):
    type = 'user'

    def __init__(self, keyword, libname):
        self.name = keyword.name
        self.keywords = keyword.keywords.normal
        self.return_value = tuple(keyword.return_)
        self.teardown = keyword.keywords.teardown
        self.libname = libname
        self.doc = unic(keyword.doc)
        self.tags = keyword.tags
        self.arguments = UserKeywordArgumentParser().parse(tuple(keyword.args),
                                                           self.longname)
        self.timeout = keyword.timeout

    @property
    def longname(self):
        return '%s.%s' % (self.libname, self.name) if self.libname else self.name

    @property
    def shortdoc(self):
        return self.doc.splitlines()[0] if self.doc else ''

    def _init_keyword(self, variables):
        # TODO: Should use runner and not change internal state like this.
        # Timeouts should also be cleaned up in general.
        doc = variables.replace_string(self.doc, ignore_errors=True)
        doc, tags = split_tags_from_doc(doc)
        self.doc = doc
        self.tags = [variables.replace_string(tag, ignore_errors=True)
                     for tag in self.tags] + tags
        if self.timeout:
            self.timeout = KeywordTimeout(self.timeout.value,
                                          self.timeout.message,
                                          variables)
        else:
            self.timeout = None

    def run(self, kw, context):
        self._init_keyword(context.variables)
        if context.dry_run:
            return UserKeywordDryRunner(self).run(kw, context)
        return UserKeywordRunner(self).run(kw, context)


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


class EmbeddedArgs(UserKeywordCall):

    def __init__(self, name, template):
        match = template.embedded_name.match(name)
        if not match:
            raise ValueError('Does not match given name')
        UserKeywordCall.__init__(self, template.keyword, template.libname)
        self.embedded_args = list(zip(template.embedded_args, match.groups()))
        self.name = name

    def run(self, kw, context):
        self._init_keyword(context.variables)
        if context.dry_run:
            return EmbeddedArgsUserKeywordDryRunner(self).run(kw, context)
        return EmbeddedArgsUserKeywordRunner(self).run(kw, context)
