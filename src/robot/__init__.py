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

"""The root of the Robot Framework package.

The command line entry points provided by the framework are exposed for
programmatic usage as follows:

  * :func:`~robot.run.run`: Function to run tests.
  * :func:`~robot.run.run_cli`: Function to run tests
    with command line argument processing.
  * :func:`~robot.rebot.rebot`: Function to post-process outputs.
  * :func:`~robot.rebot.rebot_cli`: Function to post-process outputs
    with command line argument processing.
  * :mod:`~robot.libdoc`: Module for library documentation generation.
  * :mod:`~robot.testdoc`: Module for test case documentation generation.

All the functions above can be imported like ``from robot import run``.
Functions and classes provided by the modules need to be imported like
``from robot.libdoc import libdoc_cli``.

The functions and modules listed above are considered stable. Other modules in
this package are for internal usage and may change without prior notice.

.. tip:: More public APIs are exposed by the :mod:`robot.api` package.
"""

import sys
import warnings

from robot.rebot import rebot as rebot, rebot_cli as rebot_cli
from robot.run import run as run, run_cli as run_cli
from robot.version import get_version

# Avoid warnings when using `python -m robot.run`.
# https://github.com/robotframework/robotframework/issues/2552
if not sys.warnoptions:
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="runpy")


__all__ = ["rebot", "rebot_cli", "run", "run_cli"]
__version__ = get_version()
