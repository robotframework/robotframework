
*** Settings ***

Library    Collections
Library    BuiltIn
Library    Process

Library    ./libs/ClogLevelTest.py

Documentation    "Log Level Trigger" test suite

*** Test Cases ***

Log Level Trigger
   [Documentation]    Executes the "Log Level" test (log_level.robot) with all available log levels

   ${test_info}=    Get Test Info
   Log    === [LOG_LEVEL_TRIGGER_TEST] This is test '${test_info}'

   ${error_level}=    Execute Log Level Test File    ERROR
   Should Be Equal    ${error_level}    ${0}    Test with log level 'ERROR' failed

   ${error_level}=    Execute Log Level Test File    WARN
   Should Be Equal    ${error_level}    ${0}    Test with log level 'WARN' failed

   ${error_level}=    Execute Log Level Test File    USER
   Should Be Equal    ${error_level}    ${0}    Test with log level 'USER' failed

   ${error_level}=    Execute Log Level Test File    INFO
   Should Be Equal    ${error_level}    ${0}    Test with log level 'INFO' failed

   ${error_level}=    Execute Log Level Test File    DEBUG
   Should Be Equal    ${error_level}    ${0}    Test with log level 'DEBUG' failed

   ${error_level}=    Execute Log Level Test File    TRACE
   Should Be Equal    ${error_level}    ${0}    Test with log level 'TRACE' failed

   # default log level (assumed to be INFO)
   ${error_level}=    Execute Log Level Test File
   Should Be Equal    ${error_level}    ${0}    Test with default log level failed

