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

from __future__ import with_statement
import os
from os.path import abspath, dirname, join, normpath


class HtmlTemplate(object):
    _base_dir = join(dirname(abspath(__file__)), '..', 'htmldata')

    def __init__(self, filename):
        self._path = normpath(join(self._base_dir, filename.replace('/', os.sep)))

    def __iter__(self):
        with open(self._path) as file:
            for line in file:
                yield line.rstrip()
