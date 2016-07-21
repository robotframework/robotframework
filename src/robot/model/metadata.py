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

from robot.utils import is_string, NormalizedDict, py2to3, unic


@py2to3
class Metadata(NormalizedDict):

    def __init__(self, initial=None):
        NormalizedDict.__init__(self, initial, ignore='_')

    def __setitem__(self, key, value):
        if not is_string(key):
            key = unic(key)
        if not is_string(value):
            value = unic(value)
        NormalizedDict.__setitem__(self, key, value)

    def __unicode__(self):
        return u'{%s}' % ', '.join('%s: %s' % (k, self[k]) for k in self)
