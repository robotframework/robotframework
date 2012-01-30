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

import sys

if 'pythonpathsetter' not in sys.modules:
    from robot import pythonpathsetter as _
if sys.platform.startswith('java'):
    from robot import jythonworkarounds as _

from robot.rebot import rebot, rebot_cli
from robot.run import run, run_cli
from robot.version import get_version


__all__ = ['run', 'run_cli', 'rebot', 'rebot_cli']
__version__ = get_version()
