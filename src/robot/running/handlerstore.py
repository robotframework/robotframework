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

from operator import attrgetter

from robot.errors import DataError, KeywordError
from robot.utils import NormalizedDict

from .usererrorhandler import UserErrorHandler


class HandlerStore:
    LIBRARY_TYPE = 'Library'
    TEST_CASE_FILE_TYPE = 'Test case file'
    RESOURCE_FILE_TYPE = 'Resource file'

    def __init__(self, source, source_type):
        self.source = source
        self.source_type = source_type
        self._normal = NormalizedDict(ignore='_')
        self._embedded = []

    def add(self, handler, embedded=False):
        if embedded:
            self._embedded.append(handler)
        elif handler.name not in self._normal:
            self._normal[handler.name] = handler
        else:
            error = DataError('Keyword with same name defined multiple times.')
            self._normal[handler.name] = UserErrorHandler(error, handler.name,
                                                          handler.libname)
            raise error

    def __iter__(self):
        handlers = list(self._normal.values()) + self._embedded
        return iter(sorted(handlers, key=attrgetter('name')))

    def __len__(self):
        return len(self._normal) + len(self._embedded)

    def __contains__(self, name):
        if name in self._normal:
            return True
        return any(template.matches(name) for template in self._embedded)

    def create_runner(self, name):
        return self[name].create_runner(name)

    def __getitem__(self, name):
        try:
            return self._normal[name]
        except KeyError:
            return self._find_embedded(name)

    def _find_embedded(self, name):
        embedded = [template for template in self._embedded if template.matches(name)]
        if len(embedded) == 1:
            return embedded[0]
        self._raise_no_single_match(name, embedded)

    def _raise_no_single_match(self, name, found):
        if self.source_type == self.TEST_CASE_FILE_TYPE:
            source = self.source_type
        else:
            source = "%s '%s'" % (self.source_type, self.source)
        if not found:
            raise KeywordError("%s contains no keywords matching name '%s'."
                               % (source, name))
        error = ["%s contains multiple keywords matching name '%s':"
                 % (source, name)]
        names = sorted(handler.name for handler in found)
        raise KeywordError('\n    '.join(error + names))
