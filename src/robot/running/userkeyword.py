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

from .arguments import EmbeddedArguments
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
            handler = self._create_handler(kw)
            embedded = isinstance(handler, EmbeddedArgumentsHandler)
            try:
                self.handlers.add(handler, embedded)
            except DataError as error:
                self._log_creating_failed(handler, error)

    def _create_handler(self, kw):
        if kw.embedded_args:
            return EmbeddedArgumentsHandler(kw, self.name, kw.embedded_args)
        return UserKeywordHandler(kw, self.name)

    def _log_creating_failed(self, handler, error):
        LOGGER.error(f"Error in file '{self.source}' on line {handler.lineno}: "
                     f"Creating keyword '{handler.name}' failed: {error.message}")

    def handlers_for(self, name):
        return self.handlers.get_handlers(name)


# TODO: Should be merged with running.model.UserKeyword

class UserKeywordHandler:
    supports_embedded_args = False

    def __init__(self, keyword, owner):
        self.name = keyword.name
        self.full_name = keyword.full_name
        self.short_doc = keyword.short_doc
        self.private = keyword.private
        self.owner = owner
        self.doc = keyword.doc
        self.source = keyword.source
        self.lineno = keyword.lineno
        self.tags = keyword.tags
        self.arguments = keyword.args
        self.timeout = keyword.timeout
        self.body = keyword.body
        self.error = keyword.error
        self.setup = keyword.setup if keyword.has_setup else None
        self.teardown = keyword.teardown if keyword.has_teardown else None

    def create_runner(self, name, languages=None):
        return UserKeywordRunner(self)


class EmbeddedArgumentsHandler(UserKeywordHandler):
    supports_embedded_args = True

    def __init__(self, keyword, owner, embedded):
        super().__init__(keyword, owner)
        self.embedded = embedded

    def matches(self, name):
        return self.embedded.match(name) is not None

    def create_runner(self, name, languages=None):
        return EmbeddedArgumentsRunner(self, name)
