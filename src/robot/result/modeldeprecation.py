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

from robot.model import Tags


def deprecated(method):
    def wrapper(self, *args, **kws):
        """Deprecated."""
        return method(self, *args, **kws)
    return wrapper


class DeprecatedAttributesMixin(object):
    __slots__ = []

    @property
    @deprecated
    def name(self):
        return ''

    @property
    @deprecated
    def kwname(self):
        return self.name

    @property
    @deprecated
    def libname(self):
        return None

    @property
    @deprecated
    def args(self):
        return ()

    @property
    @deprecated
    def assign(self):
        return ()

    @property
    @deprecated
    def tags(self):
        return Tags()

    @property
    @deprecated
    def timeout(self):
        return None

    @property
    @deprecated
    def message(self):
        return ''
