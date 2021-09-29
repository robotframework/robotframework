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

import os
import re
import sys


def _version_to_tuple(version_string):
    version = [int(re.match(r'\d*', v).group() or 0) for v in version_string.split('.')]
    missing = [0] * (3 - len(version))
    return tuple(version + missing)[:3]


PY_VERSION = sys.version_info[:3]
PY2 = PY_VERSION[0] == 2
PY3 = not PY2
IRONPYTHON = sys.platform == 'cli'
PYPY = 'PyPy' in sys.version
UNIXY = os.sep == '/'
WINDOWS = not UNIXY
RERAISED_EXCEPTIONS = (KeyboardInterrupt, SystemExit, MemoryError)

if sys.platform.startswith('java'):
    from java.lang import OutOfMemoryError, System

    JYTHON = True
    JAVA_VERSION = _version_to_tuple(System.getProperty('java.version'))
    RERAISED_EXCEPTIONS += (OutOfMemoryError,)

else:
    JYTHON = False
    JAVA_VERSION = (0, 0, 0)
