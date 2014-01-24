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
        self.match = MultiMatcher(self._yield_patterns(flattened)).match

    def _yield_patterns(self, flattened):
        if isinstance(flattened, basestring):
            flattened = [flattened]
        for flat in flattened:
            if not flat.upper().startswith('NAME:'):
                raise DataError("Expected pattern to start with 'NAME:' "
                                "but got '%s'." % flat)
            yield flat[5:]
