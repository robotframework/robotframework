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

from robot.errors import DataError
from robot.utils import MultiMatcher


class FlattenKeywordMatcher(object):

    def __init__(self, flattened):
        self._types = []
        names = self._yield_names_and_set_types(flattened, self._types)
        self._name_matcher = MultiMatcher(names)

    def _yield_names_and_set_types(self, flattened, types):
        if isinstance(flattened, basestring):
            flattened = [flattened]
        for flat in flattened:
            upper = flat.upper()
            if upper in ('FOR', 'FORITEM'):
                types.append(flat.lower())
            elif upper.startswith('NAME:'):
                yield flat[5:]
            else:
                raise DataError("Expected 'FOR', 'FORITEM', or "
                                "'NAME:<pattern>' but got '%s'." % flat)

    def match(self, name, type):
        return self._name_matcher.match(name) or type in self._types
