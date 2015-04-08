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

from operator import attrgetter
from os.path import splitext

from robot.errors import DataError
from robot.parsing import VALID_EXTENSIONS as RESOURCE_EXTENSIONS
from robot.utils import NormalizedDict


class HandlerStore(object):

    def __init__(self, source):
        self._source = source
        self._normal = NormalizedDict(ignore='_')
        self._embedded = []

    def add(self, handler, embedded=False):
        if embedded:
            self._embedded.append(handler)
        else:
            self._normal[handler.name] = handler

    def remove(self, name):
        if name in self._normal:
            self._normal.pop(name)
        self._embedded = [e for e in self._embedded if not e.matches(name)]

    def __iter__(self):
        return iter(sorted(self._normal.values() + self._embedded,
                           key=attrgetter('name')))

    def __len__(self):
        return len(self._normal) + len(self._embedded)

    def __contains__(self, name):
        if name in self._normal:
            return True
        return any(template.matches(name) for template in self._embedded)

    def __getitem__(self, name):
        try:
            return self._normal[name]
        except KeyError:
            return self._find_embedded(name)

    def _find_embedded(self, name):
        embedded = [template.create(name) for template in self._embedded
                    if template.matches(name)]
        if len(embedded) == 1:
            return embedded[0]
        self._raise_no_single_match(name, embedded)

    def _raise_no_single_match(self, name, found):
        if self._source is None:
            where = "Test case file"
        elif self._is_resource(self._source):
            where = "Resource file '%s'" % self._source
        else:
            where = "Test library '%s'" % self._source
        if not found:
            raise DataError("%s contains no keywords matching name '%s'."
                            % (where, name))
        error = ["%s contains multiple keywords matching name '%s':"
                 % (where, name)]
        names = sorted(handler.orig_name for handler in found)
        raise DataError('\n    '.join(error + names))

    def _is_resource(self, source):
        extension = splitext(source)[1][1:].lower()
        return extension in RESOURCE_EXTENSIONS
