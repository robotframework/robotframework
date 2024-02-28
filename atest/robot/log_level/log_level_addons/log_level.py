# **************************************************************************************************************
#
#  Copyright 2020-2024 Robert Bosch GmbH
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
#
# **************************************************************************************************************
#
# log_level.py
#
# XC-HWP/ESW3-Queckenstedt
#
# 23.02.2024
#
# --------------------------------------------------------------------------------------------------------------

# -- import standard Python modules
import sys, os, platform, shlex, subprocess

# -- import Robotframework API
from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn

# -- import test specific Python modules
from CLogData import CLogData

# --------------------------------------------------------------------------------------------------------------
#
MODULE_VERSION = "0.1.0"
#
# --------------------------------------------------------------------------------------------------------------

@library
class log_level():
    """Keyword library to call the Log keyword for all available log levels.
    """

    ROBOT_AUTO_KEYWORDS   = False # only decorated methods are keywords
    ROBOT_LIBRARY_VERSION = MODULE_VERSION
    ROBOT_LIBRARY_SCOPE   = 'GLOBAL'

    # --------------------------------------------------------------------------------------------------------------

    def __init__(self):
        self.__oLogData = CLogData()

    def __del__(self):
        pass

    # --------------------------------------------------------------------------------------------------------------

    @keyword
    def log_levels_in_python_library(self):
        """Executes the "Log" keyword with all available log levels
        """

        # -- with explicite log level
        tupleLogLevels = ("ERROR", "WARN", "USER", "INFO", "DEBUG", "TRACE")
        for sLogLevel in tupleLogLevels:
            bAck, log_message = self.__oLogData.get_single_log_message("PYTHON_LIBRARY", sLogLevel)
            if bAck is not True:
                BuiltIn().log(log_message, "ERROR")
                return bAck, log_message
            BuiltIn().log(log_message, sLogLevel)

        # -- without explicite log level (default log level assumed to be INFO)
        bAck, log_message = self.__oLogData.get_single_log_message("PYTHON_LIBRARY", "DEFAULT")
        if bAck is not True:
            BuiltIn().log(log_message, "ERROR")
            return bAck, log_message
        BuiltIn().log(log_message)

        return bAck, log_message

    # eof def log_levels_in_python_library(...):

    # --------------------------------------------------------------------------------------------------------------

# eof class log_level():

