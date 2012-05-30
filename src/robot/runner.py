#!/usr/bin/env python

#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

# Allows running as a script. __name__ check needed with multiprocessing:
# http://code.google.com/p/robotframework/issues/detail?id=1137
if 'robot' not in sys.modules and __name__ == '__main__':
    import pythonpathsetter

from robot import run_cli
from robot.output import LOGGER

LOGGER.warn("'robot/runner.py' entry point is deprecated and will be removed "
            "in Robot Framework 2.8. Use new 'robot/run.py' instead.")

if __name__ == '__main__':
    run_cli(sys.argv[1:])
