#  Copyright 2008-2014 Nokia Solutions and Networks
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

"""Implements storing and resolving variables.

This package is for internal usage only, and also subject to heavy refactoring
in the future.
"""

import os
import tempfile

from robot import utils
from robot.output import LOGGER

from .isvar import contains_var, is_var, is_scalar_var, is_list_var
from .variables import Variables
from .variableassigner import VariableAssigner
from .variablesplitter import VariableSplitter, VariableIterator


GLOBAL_VARIABLES = Variables()


def init_global_variables(settings):
    GLOBAL_VARIABLES.clear()
    _set_cli_vars(settings)
    for name, value in [ ('${TEMPDIR}', utils.abspath(tempfile.gettempdir())),
                         ('${EXECDIR}', utils.abspath('.')),
                         ('${/}', os.sep),
                         ('${:}', os.pathsep),
                         ('${\\n}', os.linesep),
                         ('${SPACE}', ' '),
                         ('${EMPTY}', ''),
                         ('@{EMPTY}', ()),
                         ('${True}', True),
                         ('${False}', False),
                         ('${None}', None),
                         ('${null}', None),
                         ('${OUTPUT_DIR}', settings['OutputDir']),
                         ('${OUTPUT_FILE}', settings['Output'] or 'NONE'),
                         ('${REPORT_FILE}', settings['Report'] or 'NONE'),
                         ('${LOG_FILE}', settings['Log'] or 'NONE'),
                         ('${LOG_LEVEL}', settings['LogLevel']),
                         ('${DEBUG_FILE}', settings['DebugFile'] or 'NONE'),
                         ('${PREV_TEST_NAME}', ''),
                         ('${PREV_TEST_STATUS}', ''),
                         ('${PREV_TEST_MESSAGE}', '') ]:
        GLOBAL_VARIABLES[name] = value


def _set_cli_vars(settings):
    for path, args in settings['VariableFiles']:
        try:
            path = utils.find_file(path, file_type='Variable file')
            GLOBAL_VARIABLES.set_from_file(path, args)
        except:
            msg, details = utils.get_error_details()
            LOGGER.error(msg)
            LOGGER.info(details)
    for varstr in settings['Variables']:
        try:
            name, value = varstr.split(':', 1)
        except ValueError:
            name, value = varstr, ''
        GLOBAL_VARIABLES['${%s}' % name] = value
