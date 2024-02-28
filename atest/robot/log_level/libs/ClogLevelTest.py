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
# ClogLevelTest.py
#
# XC-HWP/ESW3-Queckenstedt
#
# 26.02.2024
#
# --------------------------------------------------------------------------------------------------------------

# -- import standard Python modules
import sys, os, platform, shlex, subprocess

# -- import Robotframework API
from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn

# -- import test specific Python modules
from CLogData import CLogData
from CComparison import CComparison

# --------------------------------------------------------------------------------------------------------------
#
# We assume here that the version of this module is also the version of the entire "log level" test.
# Therefore the versioning happens here:
#
MODULE_NAME    = "ClogLevelTest.py"
TEST_NAME      = "log level test"
MODULE_VERSION = "0.1.0"
MODULE_DATE    = "26.02.2024"
THIS_MODULE    = f"{MODULE_NAME} v. {MODULE_VERSION} / {MODULE_DATE}"
THIS_TEST      = f"{TEST_NAME} v. {MODULE_VERSION} / {MODULE_DATE}"
#
# --------------------------------------------------------------------------------------------------------------

def normalize_path(sPath=None):
    """To give all paths an unique look&feel"""
    if sPath is not None:
        sPath = sPath.replace("\\", "/")
    return sPath

# --------------------------------------------------------------------------------------------------------------

@library
class ClogLevelTest():
    """Define all settings belonging to the "log level" test, like
* path and name of "log level" log files
* log level specific pattern to search for in log files
* log file check methods
    """

    ROBOT_AUTO_KEYWORDS   = False # only decorated methods are keywords
    ROBOT_LIBRARY_VERSION = MODULE_VERSION
    ROBOT_LIBRARY_SCOPE   = 'GLOBAL'

    # --------------------------------------------------------------------------------------------------------------

    def __init__(self):

        # log messages creation outsourced to separate module
        self.__oLogData = CLogData()

        # path and name of Robot Framework log files to check; file names depend on log level and counter value and will be computed later
        self.__sOutputFile_XML     = None
        self.__sOutputFile_LOG     = None
        self.__sOutputFile_REPORT  = None
        self.__sOutputFile_DEBUG   = None
        self.__sOutputFile_XML_REF = None
        self.__sPatternFile_XML    = None

        # enable a sorted occurrence of log files in file explorer (sorted by log level); the numbers are part of the output file names
        self.__dictLevelNumber = {}
        self.__dictLevelNumber['ERROR']   = "1"
        self.__dictLevelNumber['WARN']    = "2"
        self.__dictLevelNumber['USER']    = "3"
        self.__dictLevelNumber['INFO']    = "4"
        self.__dictLevelNumber['DEBUG']   = "5"
        self.__dictLevelNumber['TRACE']   = "6"
        self.__dictLevelNumber['DEFAULT'] = "9"

        # The meaning of "DEFAULT" in this test is: No log level defined in 'Log' keyword call.
        # Robot Framework defines the default log level; assumed to be 'INFO'. This is the mapping:
        self.dictDefaultLogLevel = {"DEFAULT" : "INFO"}

    def __del__(self):
        pass

    # --------------------------------------------------------------------------------------------------------------

    @keyword
    def get_test_info(self):
        """Returns the test information
        """
        return THIS_TEST
    # eof def get_test_info(...):

    @keyword
    def get_module_info(self):
        """Returns the module information
        """
        return THIS_MODULE
    # eof def get_module_info(...):

    # --------------------------------------------------------------------------------------------------------------

    @keyword
    def get_single_log_message(self, origin="UNKNOWN", log_level="UNKNOWN"):
        bAck, sMessage = self.__oLogData.get_single_log_message(origin, log_level)
        if bAck is not True:
            BuiltIn().log(sMessage, "ERROR")
        return bAck, sMessage

    # --------------------------------------------------------------------------------------------------------------

    @keyword
    def execute_log_level_test_file(self, log_level=None):
        """Executes the "log level" test robot file with different log levels. Also executes the output file check.
        """

        SUCCESS = 0
        ERROR   = 1

        listCommandLineParts = []
        PYTHON = sys.executable
        listCommandLineParts.append(f"\"{PYTHON}\"")
        listCommandLineParts.append("-m robot")

        if log_level is None:
            log_level = "DEFAULT" # part of output file names
        else:
            listCommandLineParts.append(f"--loglevel {log_level}")

        tupleLogLevels = self.__oLogData.get_supported_log_levels()
        if log_level not in tupleLogLevels:
            BuiltIn().log(f"Internal test error: log level '{log_level}' not in {tupleLogLevels}", "ERROR")
            return ERROR

        sLevelNumber = self.__dictLevelNumber[log_level]

        # get output dir from this Robot Framework process
        sOutputDir = normalize_path(BuiltIn().get_variable_value("${OUTPUT DIR}"))
        # derive output dir of called Robot Framework process out of output dir of this process
        sOutputDir = f"{sOutputDir}/log_level_logfiles"
        # detect the current robot file folder
        sSuiteSource = normalize_path(BuiltIn().get_variable_value("${SUITE SOURCE}"))
        sSuiteSourceFolder = os.path.dirname(sSuiteSource)
        # the robot file of the called Robot Framework process (log_level.robot) is expected to be present in same folder
        sLevelTestRobotFile = f"{sSuiteSourceFolder}/log_level.robot"
        # prepare Robot Framework command line to be executed
        listCommandLineParts.append(f"-d \"{sOutputDir}\"")
        listCommandLineParts.append(f"-o {sLevelNumber}.log_level_{log_level}.xml")
        listCommandLineParts.append(f"-l {sLevelNumber}.log_level_{log_level}_log.html")
        listCommandLineParts.append(f"-r {sLevelNumber}.log_level_{log_level}_report.html")
        listCommandLineParts.append(f"-b {sLevelNumber}.log_level_{log_level}_debug.log")
        listCommandLineParts.append(f"\"{sLevelTestRobotFile}\"")

        # In the command line above we tell the Robot Framework to store all output file within sOutputDir under certain names.
        # We also need to recover these information inside this library to have access to the output files when checking the content.
        self.__sOutputFile_XML    = f"{sOutputDir}/{sLevelNumber}.log_level_{log_level}.xml"
        self.__sOutputFile_LOG    = f"{sOutputDir}/{sLevelNumber}.log_level_{log_level}_log.html"
        self.__sOutputFile_REPORT = f"{sOutputDir}/{sLevelNumber}.log_level_{log_level}_report.html"
        self.__sOutputFile_DEBUG  = f"{sOutputDir}/{sLevelNumber}.log_level_{log_level}_debug.log"

        # reference log file corresponding to the current XML output file
        self.__sOutputFile_XML_REF = f"{sSuiteSourceFolder}/referencelogfiles/{sLevelNumber}.log_level_{log_level}-REF.xml"
        if os.path.isfile(self.__sOutputFile_XML_REF) is False:
            BuiltIn().log(f"Missing reference file '{self.__sOutputFile_XML_REF}'", "ERROR")
            return ERROR

        # pattern file for comparison of XML log files
        self.__sPatternFile_XML = f"{sSuiteSourceFolder}/referencelogfiles/log_level_pattern_XML.txt"
        if os.path.isfile(self.__sPatternFile_XML) is False:
            BuiltIn().log(f"Missing pattern file '{self.__sPatternFile_XML}'", "ERROR")
            return ERROR

        # === test part 1: execute the 'log_level' test file
        nErrorLevel  = ERROR
        sCommandLine = " ".join(listCommandLineParts)
        BuiltIn().log(f"Now executing: {sCommandLine}", "INFO")
        del listCommandLineParts
        listCommandLineParts = shlex.split(sCommandLine)
        try:
            nErrorLevel = subprocess.call(listCommandLineParts)
        except Exception as ex:
            BuiltIn().log(str(ex), "ERROR")
            nErrorLevel = ERROR
        del listCommandLineParts

        if nErrorLevel != SUCCESS:
            # premature end of test (already test file execution went wrong; no need to take a look at the output files)
            return nErrorLevel

        # === test part 2: check the output files
        #     (let's say, this belongs to the test execution; no need to introduce an additional keyword at robot file level for this)
        nErrorLevel = self.__CheckOutputFiles(log_level)

        return nErrorLevel

    # eof def execute_log_level_test_file(...):

    # --------------------------------------------------------------------------------------------------------------

    def __CheckOutputFiles(self, log_level=None):
        """Checked output files: XML file and debug log file (the HTML files are generated out of the XML file
           by the Robot Framework, therefore no separate check of HTML files).
           Check 1: Messages belonging to current trace level, are found in current output file.
           Check 2: Messages not belonging to current trace level, are not found in current output file.
        """

        # At first we need access to the expected content, computed previously:
        # self.__oLogData.get_expected_content_list(log_level, file_type)
        # But this content is what is written to the output files by the 'Log' keyword.
        # The corresponding line in output files contains content added by the Robot Framework itself: the level (log_level_label).
        # The format of this content is not the same in debug log file and in XML report file - but shall also part of the file check.
        # Here we have a file type dependency. Because of this, we add the missing and specific content here (listExpectedMessages).
        # The same with the declined content.

        SUCCESS = 0
        ERROR   = 1

        # which files to check
        tupleFilesToCheck = (self.__sOutputFile_DEBUG, self.__sOutputFile_XML)

        # --------------------------------------------------------------------------------------------------------------
        # file content check
        # --------------------------------------------------------------------------------------------------------------
        for sOutputFile in tupleFilesToCheck:

           BuiltIn().log(f"Checking file '{sOutputFile}' for messages at log level '{log_level}'", "INFO")

           # access to file
           listFileContent = []
           try:
              hOutputFile = open(sOutputFile, "r", encoding="utf-8")
              sFileContent = hOutputFile.read()
              listFileContent = sFileContent.splitlines()
           except Exception as ex:
              hOutputFile.close()
              BuiltIn().log(str(ex), "ERROR")
              return ERROR
           hOutputFile.close()

           # ==============================
           # ==== 1. check expected content
           # ==============================

           # prepare expected content / consider file type dependency
           file_type = None
           if sOutputFile.upper().endswith('.LOG'):
               file_type = "LOG"
           elif sOutputFile.upper().endswith('.XML'):
               file_type = "XML"
           listExpectedContent = self.__oLogData.get_expected_content_list(log_level, file_type)

           # debug #
           # for sExpectedContent in listExpectedContent:
               # BuiltIn().log(f"sExpectedContent: '{sExpectedContent}'", "WARN")

           for sLine in listFileContent:
               for sExpectedContent in listExpectedContent:
                   if sExpectedContent in sLine:
                       listExpectedContent.remove(sExpectedContent)
                       break
           if len(listExpectedContent) > 0:
               BuiltIn().log(f"The following log messages are missing in file '{sOutputFile}':", "ERROR")
               for sExpectedContent in listExpectedContent:
                   BuiltIn().log(f"Missing log message: '{sExpectedContent}'", "ERROR")
               return ERROR

           BuiltIn().log(f"Success: Expected content found in checked output file", "INFO")

           # ==============================
           # ==== 2. check declined content
           # ==============================

           # prepare declined content / consider file type dependency
           file_type = None
           if sOutputFile.upper().endswith('.LOG'):
               file_type = "LOG"
           elif sOutputFile.upper().endswith('.XML'):
               file_type = "XML"
           listDeclinedContent = self.__oLogData.get_declined_content_list(log_level, file_type)

           # debug #
           # for sDeclinedContent in listDeclinedContent:
               # BuiltIn().log(f"sDeclinedContent: '{sDeclinedContent}'", "WARN")

           listFoundButDeclinedContent = []
           for sLine in listFileContent:
               for sDeclinedContent in listDeclinedContent:
                   if sDeclinedContent in sLine:
                       listDeclinedContent.remove(sDeclinedContent)
                       listFoundButDeclinedContent.append(sDeclinedContent)
                       break
           if len(listFoundButDeclinedContent) > 0:
               BuiltIn().log(f"The following log messages are declined but found in file '{sOutputFile}':", "ERROR")
               for sDeclinedContent in listFoundButDeclinedContent:
                   BuiltIn().log(f"Found declined log message: '{sDeclinedContent}'", "ERROR")
               return ERROR

           BuiltIn().log(f"Success: Declined content not found in checked output file", "INFO")

        # eof for sOutputFile in tupleFilesToCheck:

        # ==================================
        # ==== 3. XML outout file comparison
        # ==================================

        # In case of the XML file is affected, a simple string check like executed before, is not enough.
        # Because of the string check searches everywhere in the log file and does not consider the XML structure.
        # Messages can appear at two positions: at any position for logged Log keyword calls and within
        # the errors section (<error> tag). To fill the gap we execute now a log file comparison.
        # Based on a pattern file (log_level_pattern_XML.txt), the current XML output file is compared with a
        # corresponding reference output file.

        oComparison = CComparison()
        bIdentical, bSuccess, sResult = oComparison.Compare(self.__sOutputFile_XML, self.__sOutputFile_XML_REF, self.__sPatternFile_XML)
        if bSuccess is not True:
            BuiltIn().log(sResult, "ERROR")
            return ERROR
        if bIdentical is False:
            BuiltIn().log(sResult, "ERROR")
            return ERROR
        BuiltIn().log(f"XML file comparison successful. {sResult}", "INFO")

        BuiltIn().log(f"Success: Content checked in output files successfully", "INFO")
        return SUCCESS

    # eof def __CheckOutputFiles(self):

    # --------------------------------------------------------------------------------------------------------------

# eof class ClogLevelTest():

