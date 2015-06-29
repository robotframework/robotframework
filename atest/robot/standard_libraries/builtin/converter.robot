*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/converter.robot
Force Tags        regression
Default Tags      jybot    pybot
Resource          atest_resource.robot

*** Variables ***
${ARG TYPES MSG}    Argument types are:\n

*** Test Cases ***
Convert To Integer
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc.kws[0].kws[0].msgs[0]}    unicode

Convert To Integer With Java Objects
    [Tags]    jybot
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc.kws[0].kws[0].msgs[0]}    java.lang.String

Convert To Integer With Base
    Check Test Case    ${TEST NAME}

Convert To Integer With Invalid Base
    Check Test Case    ${TEST NAME}

Convert To Integer With Embedded Base
    Check Test Case    ${TEST NAME}

Convert To Integer With Base And Java Objects
    [Tags]    jybot
    Check Test Case    ${TEST NAME}

Convert To Binary
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc.kws[0].kws[0].msgs[0]}    unicode

Convert To Octal
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc.kws[0].kws[0].msgs[0]}    unicode

Convert To Hex
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc.kws[0].kws[0].msgs[0]}    unicode

Convert To Number
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc.kws[0].kws[0].msgs[0]}    unicode

Convert To Number With Java Objects
    [Tags]    jybot
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc.kws[0].kws[0].msgs[0]}    java.lang.String

Convert To Number With Precision
    Check Test Case    ${TEST NAME}

Numeric conversions with long types
    Check Test Case    ${TEST NAME}

Convert To String
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode

Convert To Boolean
    ${tc}=    Check Test Case    ${TEST NAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode

Create List
    Check Test Case    ${TEST NAME}

*** Keywords ***
Verify argument type message
    [Arguments]    ${msg}    ${type1}
    Check log message    ${msg}    Argument types are:\n<type '${type1}'>    DEBUG
