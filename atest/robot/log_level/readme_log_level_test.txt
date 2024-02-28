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

XC-HWP/ESW3-Queckenstedt

28.02.2024

--------------------------------------------------------------------------------------------------------------

The "log level 'USER'" feature
==============================

The bunch of log levels provided by the Robot Framework, has been extended by a log level 'USER'.

The reason for this new log level is to have a better separation between user specific log messages
and standard messages provided by the Robot Framework itself (at default log level INFO).
A user who really wants to have his own output only, has the ability now to switch to log level USER,
at which all INFO messages (and below) from Robot Framework or other sources like Python keyword libraries
or resource files are suppressed.

This reduces the amount of content in Robot Framework output files. 

Additionally the standard output of Robot Framework has been reduced (carefully).

Example: The Robot Framework logs the start and the end of a keyword execution (under log level INFO).
But when the affected keyword is the 'Log' keyword and when this Log keyword does not produce any output
because of the log level does not fit, then it makes no sense to log the start and the end of this
keyword. Or in other words: It makes no sense to log the start and the end of something that does not have
any effect during test execution. Therefore corresponding output is suppressed now.

Also this measure reduces the amount of content in Robot Framework output files and eases the readability.

The new log level USER is placed between INFO and WARN.


The "log level" self test
=========================

A robot file, a resource file and a Python keyword library file contain Log keyword calls for every available log level.

At first the robot file executes his own Log keywords, after this the robot file executes the keyword defined in the
resource file (the keyword that contains the Log keyword calls for every available log level) and then the corresponding
keyword defined in the Python keyword library file.

The robot file itself is called by another robot file with every available log level in command line.

For every combination of log levels it is checked if all expected log messages can be found in the debug log file
and in the XML report file. Additionally it is checked if all declined log messages are not present in these files.

Additionally the XML report file is compared with a reference file (based on a pattern file). This is to consider the
XML structure and the multiple occurrences of log messages also.

Every deviation immediately stops the test.

The log files of this "log level" self test can be found in a separate output folder 'log_level_logfiles'
that is a sub folder of the output folder defined by the Robot Framework atest script run.py.

The test files of the "log level" self test are placed in 'atest\robot\log_level'.


Message string structure
------------------------

Every message written by the self test, has the following structure:

=== [<unique identifier>] - [<origin>] - [<log level>]: <test string>

Example:

=== [LOG_LEVEL_TEST] - [ROBOT_FILE] - [ERROR]: "ERROR test string ERROR test string ERROR test string ERROR"

* <unique identifier>
  The <unique identifier> is "LOG_LEVEL_TEST". Every line contains this string.

* <origin>
  <origin> is one of ("ROBOT_FILE", "RESOURCE_FILE", "PYTHON_LIBRARY") and belongs to the position of the Log keyword
  that produces this this line of output.

* <log level>
  <log level> is the log level, the message belongs to.

* <test string>
  <test string> is a simple test string with some dummy content and contains also the log level.

With this naming convention every self test log message is individual and therefore can be detected in output files easily.


Self test files:
----------------

* log_level.robot

  Contains Log keyword calls for all available log levels and the keyword calls from resource file and Python keyword library.

* log_level_addons/log_level.resource

  Contains Log keyword calls for all available log levels

* log_level_addons/log_level.py

  Contains Log keyword calls for all available log levels

* log_level_trigger.robot

  Executes log_level.robot with all available log levels and checks the resulting output files.

* libs/ClogLevelTest.py

  Keyword library to support the self test. Responsible for:
  - versioning
  - definition of all output files and folders belonging to the self test
  - execution of log_level.robot
  - check of output (log messages in output files)

* libs/CLogData.py

  Pure Python module to define and manage the log message strings used by the self test.
  Background is to have the log message strings defined at one single position only.

  The log message strings defined in this module, are used twice: as Log keyword parameter
  and also as string to search for in output files.

* libs/CComparison.py

  Pure Python module containing the file comparison mechanism.
  Origin: https://github.com/test-fullautomation/python-extensions-collection

* referencelogfiles/*.xml

  Reference files used for output file copmarison of XML report files

* referencelogfiles/log_level_pattern_XML.txt

  Pattern file with regular expressions used for output file comparison


Self test execution:
--------------------

<Python interpreter> "./atest/run.py" "./atest/robot/log_level"

Caution: run.py is CWD sensitive!




