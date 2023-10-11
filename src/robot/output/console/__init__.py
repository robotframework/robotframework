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
import warnings
from importlib.metadata import entry_points

from robot.errors import DataError

from .dotted import DottedOutput
from .quiet import NoOutput, QuietOutput
from .verbose import VerboseOutput

ENTRY_POINT_GROUP = 'robot.output.console'


def ConsoleOutput(type='verbose', width=78, colors='AUTO', markers='AUTO',
                  stdout=None, stderr=None):
    upper = type.upper()
    if upper == 'VERBOSE':
        return VerboseOutput(width, colors, markers, stdout, stderr)
    if upper == 'DOTTED':
        return DottedOutput(width, colors, stdout, stderr)
    if upper == 'QUIET':
        return QuietOutput(colors, stderr)
    if upper == 'NONE':
        return NoOutput()

    discoveries = entry_points(group=ENTRY_POINT_GROUP, name=type)

    if discoveries:
        if len(discoveries) > 1:
            warnings.warn("Multiple console outputs with name '%s' found. "
                          "Using first entry (%s)."
                          % (type, discoveries[0].value))

        constructor = discoveries[0].load()
        return constructor(width, colors, markers, stdout, stderr)

    values = ["VERBOSE", "DOTTED", "QUIET", "NONE"]
    discoveries = entry_points(group=ENTRY_POINT_GROUP)
    values.extend(discovery.name for discovery in discoveries)

    raise DataError("Invalid console output type '%s'. Available: %s."
                    % (type, ', '.join(values)))
