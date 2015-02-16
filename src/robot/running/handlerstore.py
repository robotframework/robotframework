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

from robot.errors import DataError
from robot.utils import NormalizedDict, seq2str


class HandlerStore(object):

    def __init__(self, source):
        self._source = source
        self._handlers = NormalizedDict(ignore='_')
        self._embedded = []

    def add(self, handler, embedded=False):
        self._handlers[handler.name] = handler
        if embedded:
            self._embedded.append(handler)

    def __iter__(self):
        return self._handlers.itervalues()

    def __len__(self):
        return len(self._handlers)

    def __contains__(self, name):
        if name in self._handlers:
            return True
        for template in self._embedded:
            if template.matches(name):
                return True
        return False

    def __getitem__(self, name):
        try:
            return self._handlers[name]
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
        else:
            where = "Resource file '%s'" % self._source
        if not found:
            raise DataError("%s contains no keywords matching name '%s'."
                            % (where, name))
        error = ["%s contains multiple keywords matching name '%s':"
                 % (where, name)]
        names = sorted(handler.orig_name for handler in found)
        raise DataError('\n    '.join(error + names))
