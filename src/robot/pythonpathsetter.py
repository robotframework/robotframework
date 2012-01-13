#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

"""Module that adds directories needed by Robot to sys.path when imported."""

import sys
import fnmatch
from os.path import abspath, dirname, join

ROBOTDIR = dirname(abspath(__file__))
PARENTDIR = dirname(ROBOTDIR)

def add_path(path, end=False):
    if not end:
        sys.path.insert(0, path)
    else:
        sys.path.append(path)

def remove_path(path):
    sys.path = [p for p in sys.path if not fnmatch.fnmatch(p, path)]


add_path(PARENTDIR)
add_path(join(ROBOTDIR, 'libraries'))
add_path('.', end=True)  # Jython adds this automatically so let's be consistent
remove_path(ROBOTDIR)    # Prevent importing internal modules directly
