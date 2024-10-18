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

# -- import standard Python modules
import sys, os

# --------------------------------------------------------------------------------------------------------------
# In the context of the "log_level" test, message strings are written by three sources (origin):
# 1. robot file
# 2. resource file
# 3. Python keyword library file
# In all three cases the output must fit to the log level rules
# --------------------------------------------------------------------------------------------------------------
# message string structure:
#
# === [<unique identifier>] - [<origin>] - [<log level>]: <test string>
# Example:
# === [LOG_LEVEL_TEST] - [ROBOT_FILE] - [ERROR]: "ERROR test string ERROR test string ERROR test string ERROR"
# --------------------------------------------------------------------------------------------------------------
 
class CLogData():

    def __init__(self):

        # where the Log keyword calls are located
        self.__tupleOrigins = ("ROBOT_FILE", "RESOURCE_FILE", "PYTHON_LIBRARY")

        # log levels supported by this test
        self.__tupleLogLevels = ("ERROR", "WARN", "USER", "INFO", "DEBUG", "TRACE", "DEFAULT")

        # The meaning of "DEFAULT" in this test is: No log level defined in 'Log' keyword call.
        # Robot Framework defines the default log level; assumed to be 'INFO'.
        self.dictDefaultLogLevel = {"DEFAULT" : "INFO"}

        # ---- log level dependent test strings
        self.__dictTestStrings = {}
        for sLogLevel in self.__tupleLogLevels:
            self.__dictTestStrings[sLogLevel] = f"{sLogLevel} test string {sLogLevel} test string {sLogLevel} test string {sLogLevel}"

        # ---- log level dependent expected levels in output files
        self.__dictExpectedLevels = {}
        self.__dictExpectedLevels["ERROR"]   = ("ERROR",)
        self.__dictExpectedLevels["WARN"]    = ("ERROR", "WARN")
        self.__dictExpectedLevels["USER"]    = ("ERROR", "WARN", "USER")
        self.__dictExpectedLevels["INFO"]    = ("ERROR", "WARN", "USER", "INFO", "DEFAULT")
        self.__dictExpectedLevels["DEBUG"]   = ("ERROR", "WARN", "USER", "INFO", "DEBUG", "DEFAULT")
        self.__dictExpectedLevels["TRACE"]   = ("ERROR", "WARN", "USER", "INFO", "DEBUG", "TRACE", "DEFAULT")
        self.__dictExpectedLevels["DEFAULT"] = ("ERROR", "WARN", "USER", "INFO", "DEFAULT")

        # ---- log level dependent declined levels in output files
        self.__dictDeclinedLevels = {}
        self.__dictDeclinedLevels["ERROR"]   = ("WARN", "USER", "INFO", "DEBUG", "TRACE", "DEFAULT")
        self.__dictDeclinedLevels["WARN"]    = ("USER", "INFO", "DEBUG", "TRACE", "DEFAULT")
        self.__dictDeclinedLevels["USER"]    = ("INFO", "DEBUG", "TRACE", "DEFAULT")
        self.__dictDeclinedLevels["INFO"]    = ("DEBUG", "TRACE")
        self.__dictDeclinedLevels["DEBUG"]   = ("TRACE",)
        self.__dictDeclinedLevels["TRACE"]   = ()
        self.__dictDeclinedLevels["DEFAULT"] = ("DEBUG", "TRACE")

    def __del__(self):
        pass

    def get_supported_log_levels(self):
        return self.__tupleLogLevels

    # content used in Log keywords
    def get_single_log_message(self, origin="UNKNOWN", log_level="DEFAULT"):
        if origin not in self.__tupleOrigins:
            sMessage = f"Origin '{origin}' not supported by this self test. Expected one of [" + ", ".join(self.__tupleOrigins) + "]"
            return False, sMessage
        if log_level not in self.__tupleLogLevels:
            sMessage = f"Log level '{log_level}' not supported by this self test. Expected one of [" + ", ".join(self.__tupleLogLevels) + "]"
            return False, sMessage
        dictLogMessages = self.get_log_messages(origin)
        return True, dictLogMessages[log_level]

    def get_log_messages(self, origin="UNKNOWN"):
        """Returns a dictionary of log messages for a certain origin.
           'origin' can be a robot file, a resource file or a Python keyword library.
        """
        dictLogMessages = {}
        for sLogLevel in self.__tupleLogLevels:
            dictLogMessages[sLogLevel] = f"=== [LOG_LEVEL_TEST] - [{origin}] - [{sLogLevel}]: {self.__dictTestStrings[sLogLevel]}"
        return dictLogMessages
    # eof def get_log_messages(...):

    def get_expected_content_list(self, log_level="DEFAULT", file_type=None):
        """Returns a list of expected log messages for a certain origin and a certain log level.
           'origin' can be a robot file, a resource file or a Python keyword library.
        """

        listExpectedContent = []

        if file_type not in ("LOG", "XML"):
            return listExpectedContent

        tupleExpectedLevels = self.__dictExpectedLevels[log_level]

        for origin in self.__tupleOrigins:
            dictLogMessages = self.get_log_messages(origin)
            for sLevel in tupleExpectedLevels:
                # Put together the part from Robot Framework (the log level label)
                # and the part from this test (the log messages).
                # The format of the log level label in output files depends on the file type.
                log_level_label = sLevel
                if sLevel == "DEFAULT":
                    log_level_label = self.dictDefaultLogLevel[sLevel]
                sExpectedContent = ""
                if file_type == "LOG":
                    sExpectedContent = f"- {log_level_label} - {dictLogMessages[sLevel]}"
                elif file_type == "XML":
                    sExpectedContent = f"level=\"{log_level_label}\">{dictLogMessages[sLevel]}"
                listExpectedContent.append(sExpectedContent)
            # eof for sLevel in tupleExpectedLevels:
        # eof for origin in self.__tupleOrigins:

        return listExpectedContent
    # eof def get_expected_content_list(...):

    def get_declined_content_list(self, log_level="DEFAULT", file_type=None):
        """Returns a list of declined log messages for a certain origin and a certain log level.
           'origin' can be a robot file, a resource file or a Python keyword library.
        """

        listDeclinedContent = []

        if file_type not in ("LOG", "XML"):
            return listDeclinedContent

        tupleDeclinedLevels = self.__dictDeclinedLevels[log_level]

        for origin in self.__tupleOrigins:
            dictLogMessages = self.get_log_messages(origin)
            for sLevel in tupleDeclinedLevels:
                # Put together the part from Robot Framework (the log level label)
                # and the part from this test (the log messages).
                # The format of the log level label in output files depends on the file.
                log_level_label = sLevel
                if sLevel == "DEFAULT":
                    log_level_label = self.dictDefaultLogLevel[sLevel]
                sDeclinedContent = ""
                if file_type == "LOG":
                    sDeclinedContent = f"- {log_level_label} - {dictLogMessages[sLevel]}"
                    listDeclinedContent.append(sDeclinedContent)
                elif file_type == "XML":
                    if sLevel not in ("ERROR", "WARN"):
                        # errors and warnings are always content of XML file - and therefore not declined
                        sDeclinedContent = f"level=\"{log_level_label}\">{dictLogMessages[sLevel]}"
                        listDeclinedContent.append(sDeclinedContent)
            # eof for sLevel in tupleDeclinedLevels:
        # eof for origin in self.__tupleOrigins:

        return listDeclinedContent
    # eof def get_declined_content_list(...):

# eof class CLogData():
