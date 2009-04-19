#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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
import os
import fnmatch


def norm_path(path):
    path = os.path.normpath(path)
    # If windows or cyqwin (os.path.normcase not supported in jython)
    if os.sep == '\\' or sys.platform.count('cygwin') > 0:
        path = path.lower()
    return path

def add_path(path, to_beginning=False):
    if not path:
        return
    path = norm_path(path)
    if path not in sys.path and os.path.exists(path):
        if to_beginning:
            sys.path.insert(0, path)
        else:
            sys.path.append(path)
                
def remove_path(path):
    path = norm_path(path)
    while path in sys.path:
        sys.path.remove(path)


sys.path = [ norm_path(p) for p in sys.path ]

ROBOTDIR = norm_path(os.path.dirname(os.path.abspath(__file__)))
PARENTDIR = os.path.dirname(ROBOTDIR)

add_path(os.path.join(ROBOTDIR, 'libraries'), to_beginning=True)
add_path(PARENTDIR, to_beginning=True)
# Handles egg installations
if fnmatch.fnmatchcase(os.path.basename(PARENTDIR), 'robotframework-*.egg'):
    add_path(os.path.dirname(PARENTDIR), to_beginning=True)

# Remove ROBOTDIR dir to disallow importing robot internal modules directly
remove_path(ROBOTDIR)

# Elements from PYTHONPATH. By default it is not processed in Jython and in
# Python valid non-absolute paths may be ignored.
PYPATH = os.environ.get('PYTHONPATH')
if PYPATH:
    for path in PYPATH.split(os.pathsep):
        add_path(path)
    del path

# Current dir (it seems to be in Jython by default so let's be consistent)
add_path('.')

del norm_path, add_path, remove_path, ROBOTDIR, PARENTDIR, PYPATH
