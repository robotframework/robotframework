#  Copyright 2008 Nokia Siemens Networks Oyj
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


import os

from robot import utils

from variables import Variables
from isvar import is_var, is_scalar_var, is_list_var


GLOBAL_VARIABLES = Variables()


def init_global_variables(settings, syslog):
    _set_cli_vars(settings, syslog)
    for name, value in [ ('${TEMPDIR}', utils.get_temp_dir()),
                         ('${/}', os.sep), 
                         ('${:}', os.pathsep),
                         ('${SPACE}', ' '),
                         ('${EMPTY}', ''),
                         ('${OUTPUT_DIR}', settings['OutputDir']),
                         ('${OUTPUT_FILE}', settings['Output']),
                         ('${SUMMARY_FILE}', settings['Summary']),
                         ('${REPORT_FILE}', settings['Report']),
                         ('${LOG_FILE}', settings['Log']),
                         ('${DEBUG_FILE}', settings['DebugFile']),
                         ('${PREV_TEST_NAME}', ''),
                         ('${PREV_TEST_STATUS}', ''),
                         ('${PREV_TEST_MESSAGE}', '') ]:
        GLOBAL_VARIABLES[name] = value

def _set_cli_vars(settings, syslog):
    for varfile in settings['VariableFiles']:
        GLOBAL_VARIABLES.set_from_file(varfile, [], syslog)
    for varstr in settings['Variables']:
        try:
            name, value = varstr.split(':', 1)
        except ValueError:
            name, value = varstr, ''
        GLOBAL_VARIABLES['${%s}' % name] = value
