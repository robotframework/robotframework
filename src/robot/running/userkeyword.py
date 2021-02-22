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
from robot.utils import getshortdoc, unic

from .arguments import EmbeddedArguments, UserKeywordArgumentParser
from .handlerstore import HandlerStore
from .userkeywordrunner import UserKeywordRunner, EmbeddedArgumentsRunner
from .usererrorhandler import UserErrorHandler


class UserLibrary(object):
    TEST_CASE_FILE_TYPE = HandlerStore.TEST_CASE_FILE_TYPE
    RESOURCE_FILE_TYPE = HandlerStore.RESOURCE_FILE_TYPE

    def __init__(self, resource, source_type=RESOURCE_FILE_TYPE):
        source = resource.source
        basename = os.path.basename(source) if source else None
        self.name = os.path.splitext(basename)[0] \
            if source_type == self.RESOURCE_FILE_TYPE else None
        self.doc = resource.doc
        self.handlers = HandlerStore(basename, source_type)
        self.source = source
        self.source_type = source_type
        for kw in resource.keywords:
            try:
                handler = self._create_handler(kw)
            except DataError as error:
                handler = UserErrorHandler(error, kw.name, self.name)
                self._log_creating_failed(handler, error)
            embedded = isinstance(handler, EmbeddedArgumentsHandler)
            try:
                self.handlers.add(handler, embedded)
            except DataError as error:
                self._log_creating_failed(handler, error)

    def _create_handler(self, kw):
        embedded = EmbeddedArguments(kw.name)
        if not embedded:
            return UserKeywordHandler(kw, self.name)
        if kw.args:
            raise DataError('Keyword cannot have both normal and embedded arguments.')
        return EmbeddedArgumentsHandler(kw, self.name, embedded)

    def _log_creating_failed(self, handler, error):
        LOGGER.error("Error in %s '%s': Creating keyword '%s' failed: %s"
                     % (self.source_type.lower(), self.source,
                        handler.name, error.message))


# TODO: Should be merged with running.model.UserKeyword

class UserKeywordHandler(object):

    def __init__(self, keyword, libname):
        self.name = keyword.name
        self.libname = libname
        self.doc = unic(keyword.doc)
        self.source = keyword.source
        self.lineno = keyword.lineno
        self.tags = keyword.tags
        self.arguments = UserKeywordArgumentParser().parse(tuple(keyword.args),
                                                           self.longname)
        self._kw = keyword
        self.timeout = keyword.timeout
        self.body = keyword.body
        self.return_value = tuple(keyword.return_)
        self.teardown = keyword.teardown

    @property
    def longname(self):
        return '%s.%s' % (self.libname, self.name) if self.libname else self.name

    @property
    def shortdoc(self):
        return getshortdoc(self.doc)

    def create_runner(self, name):
        return UserKeywordRunner(self)


class EmbeddedArgumentsHandler(UserKeywordHandler):

    def __init__(self, keyword, libname, embedded):
        UserKeywordHandler.__init__(self, keyword, libname)
        self.keyword = keyword
        self.embedded_name = embedded.name
        self.embedded_args = embedded.args

    def matches(self, name):
        return self.embedded_name.match(name) is not None

    def create_runner(self, name):
        return EmbeddedArgumentsRunner(self, name)
