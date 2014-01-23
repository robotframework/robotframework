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

"""Module that adds directories needed by Robot to sys.path when imported."""

import os
import sys
import fnmatch
from os.path import abspath, dirname, join

ROBOTDIR = dirname(abspath(__file__))

def add_path(path, end=False):
    if not end:
        remove_path(path)
        sys.path.insert(0, path)
    elif not any(fnmatch.fnmatch(p, path) for p in sys.path):
        sys.path.append(path)

def remove_path(path):
    sys.path = [p for p in sys.path if not fnmatch.fnmatch(p, path)]


# When, for example, robot/run.py is executed as a script, the directory
# containing the robot module is not added to sys.path automatically but
# the robot directory itself is. Former is added to allow importing
# the module and the latter removed to prevent accidentally importing
# internal modules directly.
add_path(dirname(ROBOTDIR))
remove_path(ROBOTDIR)

# Default library search locations.
add_path(join(ROBOTDIR, 'libraries'))
add_path('.', end=True)

# Support libraries/resources in PYTHONPATH also with Jython and IronPython.
for item in os.getenv('PYTHONPATH', '').split(os.pathsep):
    add_path(abspath(item), end=True)

