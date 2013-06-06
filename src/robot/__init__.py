#  Copyright 2008-2013 Nokia Siemens Networks Oyj
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

"""
The modules inside this package implement all the executables provided by
Robot Framework.

Class :py:class:`robot.run.RobotFramework` provides both
:py:func:`command line <robot.run.run_cli>` and
:py:func:`programmatic <robot.run.run>` entry points for
executing Robot Framework tests.

Similarly, classes :py:class:`robot.rebot.Rebot`,
:py:class:`robot.tidy.TidyCommandLine`, :py:class:`robot.libdoc.LibDoc`
and :py:class:`robot.testdoc.TestDoc` implement both the command line and
programmatic entry points for Rebot, Tidy, Libdoc and Testdoc.

Module :py:mod:`robot.jarrunner` wraps all the command line
entry points and acts a runner for standalone JAR distribution.

Module :py:mod:`robot.errors` takes care of the error handling within
the whole framework.
"""

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
