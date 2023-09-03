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

import os

from robot.errors import DataError
from robot.output import LOGGER
from robot.utils import getshortdoc

from .arguments import EmbeddedArguments, UserKeywordArgumentParser
from .handlerstore import HandlerStore
from .userkeywordrunner import UserKeywordRunner, EmbeddedArgumentsRunner
from .usererrorhandler import UserErrorHandler


class UserLibrary:

    def __init__(self, resource, resource_file=True):
        source = resource.source
        basename = os.path.basename(source) if source else None
        self.name = os.path.splitext(basename)[0] if resource_file else None
        self.doc = resource.doc
        self.handlers = HandlerStore()
        self.source = source
        for kw in resource.keywords:
            try:
                handler = self._create_handler(kw)
            except DataError as error:
                handler = UserErrorHandler(error, kw.name, self.name, source, kw.lineno)
                self._log_creating_failed(handler, error)
            embedded = isinstance(handler, EmbeddedArgumentsHandler)
            try:
                self.handlers.add(handler, embedded)
            except DataError as error:
                self._log_creating_failed(handler, error)

    def _create_handler(self, kw):
        if kw.error:
            raise DataError(kw.error)
        embedded = EmbeddedArguments.from_name(kw.name)
        if not embedded:
            return UserKeywordHandler(kw, self.name)
        return EmbeddedArgumentsHandler(kw, self.name, embedded)

    def _log_creating_failed(self, handler, error):
        LOGGER.error(f"Error in file '{self.source}' on line {handler.lineno}: "
                     f"Creating keyword '{handler.name}' failed: {error.message}")

    def handlers_for(self, name):
        return self.handlers.get_handlers(name)


# TODO: Should be merged with running.model.UserKeyword

class UserKeywordHandler:
    supports_embedded_args = False

    def __init__(self, keyword, libname):
        self.name = keyword.name
        self.libname = libname
        self.doc = keyword.doc
        self.source = keyword.source
        self.lineno = keyword.lineno
        self.tags = keyword.tags
        self.arguments = UserKeywordArgumentParser().parse(tuple(keyword.args),
                                                           self.longname)
        self.timeout = keyword.timeout
        self.body = keyword.body
        self.return_value = tuple(keyword.return_)
        self.teardown = keyword.teardown if keyword.has_teardown else None

    @property
    def longname(self):
        return '%s.%s' % (self.libname, self.name) if self.libname else self.name

    @property
    def shortdoc(self):
        return getshortdoc(self.doc)

    @property
    def private(self):
        return bool(self.tags and self.tags.robot('private'))

    def create_runner(self, name, languages=None):
        return UserKeywordRunner(self)


class EmbeddedArgumentsHandler(UserKeywordHandler):
    supports_embedded_args = True

    def __init__(self, keyword, libname, embedded):
        super().__init__(keyword, libname)
        self.embedded = embedded

    def matches(self, name):
        return self.embedded.match(name) is not None

    def create_runner(self, name, languages=None):
        return EmbeddedArgumentsRunner(self, name)
