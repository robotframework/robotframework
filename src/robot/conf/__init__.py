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

"""This package implements settings for both test execution and
output processing.

This package contains classes :py:class:`robot.conf.settings.RobotSettings`
and :py:class:`robot.conf.settings.RebotSettings` used internally by
Robot Framework. There should be no need to use these classes in own
implementations as each :py:mod:`public api <robot.api>` is configured
by its own settings.
"""

from .settings import RobotSettings, RebotSettings
