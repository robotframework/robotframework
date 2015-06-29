#  Copyright 2008-2015 Nokia Solutions and Networks
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

from robot.errors import DataError

from .dotted import DottedOutput
from .quiet import NoOutput, QuietOutput
from .verbose import VerboseOutput


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
    raise DataError("Invalid console output type '%s'. Available "
                    "'VERBOSE', 'DOTTED', 'QUIET' and 'NONE'." % type)
