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
import sys


JYTHON = sys.platform.startswith('java')
IRONPYTHON = sys.platform == 'cli'
PYPY = 'PyPy' in sys.version
PYTHON = not (JYTHON or IRONPYTHON)  # PyPY and CPython work mostly same way
PY2 = sys.version_info[0] == 2
PY3 = not PY2
UNIXY = os.sep == '/'
WINDOWS = not UNIXY

RERAISED_EXCEPTIONS = (KeyboardInterrupt, SystemExit, MemoryError)
if JYTHON:
    from java.lang import OutOfMemoryError
    RERAISED_EXCEPTIONS += (OutOfMemoryError,)
