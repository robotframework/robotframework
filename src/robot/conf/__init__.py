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

"""Implements settings for both test execution and output processing.

This package implements :class:`~robot.conf.settings.RobotSettings` and
:class:`~robot.conf.settings.RebotSettings` classes used internally by
the framework. There should be no need to use these classes externally.

This package can be considered relatively stable. Aforementioned classes
are likely to be rewritten at some point to be more convenient to use.
Instantiating them is not likely to change, though.
"""

from .settings import RobotSettings, RebotSettings
