#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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


import os.path


class IdGenerator:

    def __init__(self, padding=6):
        self._pattern = '%%s%%0%dd' % padding
        self._ids = {}

    def get_id(self, type_=''):
        if not self._ids.has_key(type_):
            self._ids[type_] = 0
        self._ids[type_] += 1
        return self._pattern % (type_, self._ids[type_])

    def get_prev(self, type_=''):
        return self._pattern % (type_, self._ids[type_])


class FileNameGenerator:

    def __init__(self, basename):
        self._name, self._ext = os.path.splitext(basename)
        self._idgen = IdGenerator(padding=3)

    def get_name(self):
        return self._get_name(self._idgen.get_id())

    def get_prev(self):
        return self._get_name(self._idgen.get_prev())

    def get_base(self):
        return self._name + self._ext

    def _get_name(self, id_):
        return '%s-%s%s' % (self._name, id_, self._ext)
