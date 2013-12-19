#  Copyright 2008-2013 Nokia Siemens Networks Oyj
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

import sys

from robot.utils.setter import SetterAwareType


class ModelObject(object):
    __slots__ = []
    __metaclass__ = SetterAwareType

    def __unicode__(self):
        return self.name

    def __str__(self):
        if sys.version_info[0] == 3:
            return self.__unicode__()
        return unicode(self).encode('ASCII', 'replace')

    if sys.version_info[0] == 3:
        def __bytes__(self):
            return str(self).encode('ASCII', 'replace')

    def __repr__(self):
        return repr(str(self))
