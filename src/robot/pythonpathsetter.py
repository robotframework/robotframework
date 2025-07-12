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

"""Modifies `sys.path` if Robot Framework's entry points are run as scripts.

When, for example, `robot/run.py` or `robot/libdoc.py` is executed as a script,
the `robot` directory is in `sys.path` but its parent directory is not.
Importing this module adds the parent directory to `sys.path` to make it
possible to import the `robot` module. The `robot` directory itself is removed
to prevent importing internal modules directly.

Does nothing if the `robot` module is already imported.
"""

import sys
from pathlib import Path


def set_pythonpath():
    robot_dir = Path(__file__).absolute().parent  # zipsafe
    sys.path = [str(robot_dir.parent)] + [p for p in sys.path if Path(p) != robot_dir]
