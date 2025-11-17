*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/converter.robot
Resource          atest_resource.robot

*** Test Cases ***
Convert To Integer
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc[0, 0, 0]}

Convert To Integer With Base
    Check Test Case    ${TEST NAME}

Convert To Integer With Invalid Base
    Check Test Case    ${TEST NAME}

Convert To Integer With Embedded Base
    Check Test Case    ${TEST NAME}

Convert To Binary
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc[0, 0, 0]}

Convert To Octal
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc[0, 0, 0]}

Convert To Hex
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc[0, 0, 0]}

Convert To Number
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc[0, 0, 0]}

Convert To Number With Precision
    Check Test Case    ${TEST NAME}

Numeric conversions with long types
    Check Test Case    ${TEST NAME}

Convert To String
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc[0, 0, 0, 0]}    str
    Verify argument type message    ${tc[0, 2, 0, 0]}    int

Convert To String NFC normalizes
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc[0, 0]}    str

Convert To Boolean
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc[0, 0, 0, 0]}    str
    Verify argument type message    ${tc[0, 6, 0, 0]}    int

Create List
    Check Test Case    ${TEST NAME}

*** Keywords ***
Verify argument type message
    [Arguments]    ${msg}    ${type}=str
    Check log message    ${msg}    Argument types are:\n<class '${type}'>    DEBUG
