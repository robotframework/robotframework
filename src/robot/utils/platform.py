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


PY_VERSION = sys.version_info[:3]
PYPY = 'PyPy' in sys.version
UNIXY = os.sep == '/'
WINDOWS = not UNIXY
RERAISED_EXCEPTIONS = (KeyboardInterrupt, SystemExit, MemoryError)

# Part of the deprecated Python 2/3 compatibility layer. For more details see
# the comment in `utils/__init__.py`. This constant was added to support
# SSHLibrary: https://github.com/robotframework/SSHLibrary/issues/401
PY2 = False


def isatty(stream):
    # first check if buffer was detached
    if hasattr(stream, 'buffer') and stream.buffer is None:
        return False
    if not hasattr(stream, 'isatty'):
        return False
    try:
        return stream.isatty()
    except ValueError:  # Occurs if file is closed.
        return False
