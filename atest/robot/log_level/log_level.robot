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
# Test file log_level.robot with Log keyword calls for all available log levels.
#
# This file is executed by log_level_trigger.robot with all available log levels.
#
# --------------------------------------------------------------------------------------------------------------

*** Settings ***

Library    Collections
Library    BuiltIn

Library    ./libs/ClogLevelTest.py

# execution of Log keyword in resource file
Resource    ./log_level_addons/log_level.resource

# execution of Log keyword in Python keyword library
Library    ./log_level_addons/log_level.py

Documentation    "log_level" test suite

# --------------------------------------------------------------------------------------------------------------

*** Test Cases ***

# TODO: Read from Python keyword library

# Get Single Log Message:
# * parameter 1: the origin of the 'Log' keyowrd; one of "ROBOT_FILE", "RESOURCE_FILE", "PYTHON_LIBRARY"
# * parameter 2: the log level of the 'Log' keyowrd

Log Level Test
   [Documentation]    Executes the "Log" keyword with all available log levels

   # -- with explicite log level

   ${bAck}    ${log_message}=    Get Single Log Message    ROBOT_FILE    ERROR
   Should Be Equal    ${bAck}    ${True}    Failed to execute the log level robot file
   Log    ${log_message}    ERROR

   ${bAck}    ${log_message}=    Get Single Log Message    ROBOT_FILE    WARN
   Should Be Equal    ${bAck}    ${True}    Failed to execute the log level robot file
   Log    ${log_message}    WARN

   ${bAck}    ${log_message}=    Get Single Log Message    ROBOT_FILE    USER
   Should Be Equal    ${bAck}    ${True}    Failed to execute the log level robot file
   Log    ${log_message}    USER

   ${bAck}    ${log_message}=    Get Single Log Message    ROBOT_FILE    INFO
   Should Be Equal    ${bAck}    ${True}    Failed to execute the log level robot file
   Log    ${log_message}    INFO

   ${bAck}    ${log_message}=    Get Single Log Message    ROBOT_FILE    DEBUG
   Should Be Equal    ${bAck}    ${True}    Failed to execute the log level robot file
   Log    ${log_message}    DEBUG

   ${bAck}    ${log_message}=    Get Single Log Message    ROBOT_FILE    TRACE
   Should Be Equal    ${bAck}    ${True}    Failed to execute the log level robot file
   Log    ${log_message}    TRACE

   # -- without explicite log level (default log level assumed to be INFO)

   ${bAck}    ${log_message}=    Get Single Log Message    ROBOT_FILE    DEFAULT
   Should Be Equal    ${bAck}    ${True}    Failed to execute the log level robot file
   Log    ${log_message}


   # -- the same again, but now by a keyword defined within an imported resource file
   # (valuation done within resource file)

   Log Levels In Resource File


   # -- the same again, but now by a keyword defined within an imported Python keyword library

   ${bAck}    ${log_message}=    Log Levels In Python Library
   Should Be Equal    ${bAck}    ${True}    Failed to execute the Python keyword library

# **************************************************************************************************************

