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

"""Implements the core test execution logic.

The code in this package is in many places suboptimal and likely to change in
RF 2.8. External code should use this package with care.

Currently, the main entry point is the :func:`~.model.TestSuite` factory
method.
"""

from .model import TestSuite
from .keywords import Keyword
from .testlibraries import TestLibrary
from .runkwregister import RUN_KW_REGISTER
from .signalhandler import STOP_SIGNAL_MONITOR
from .context import EXECUTION_CONTEXTS


def UserLibrary(path):
    """Create a user library instance from given resource file.

    This is used at least by libdoc.py."""
    from robot.parsing import ResourceFile
    from robot import utils
    from .arguments import UserKeywordArguments
    from .userkeyword import UserLibrary as RuntimeUserLibrary

    resource = ResourceFile(path).populate()
    ret = RuntimeUserLibrary(resource.keyword_table.keywords, path)
    for handler in ret.handlers.values(): # This is done normally only at runtime.
        handler.arguments = UserKeywordArguments(handler._keyword_args,
                                                 handler.longname)
        handler.doc = utils.unescape(handler._doc)
    ret.doc = resource.setting_table.doc.value
    return ret

