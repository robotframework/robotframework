*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    core/timeouts_with_custom_messages.robot
Resource          atest_resource.robot

*** Variables ***
${DEPRECATED}     Using custom timeout messages is deprecated since Robot Framework 3.0.1 and will be removed in future versions.

*** Test Cases ***
Default Test Timeout Message
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    My customized default test timeout    FAIL
    Custom message should be deprecated with Test Timeout    0    My customized \${DEFAULT END}

Test Timeout Message
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    My test timeout message    FAIL
    Custom message should be deprecated with [Timeout] in tests    1    My test timeout message

Test Timeout Message In Multiple Columns
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    My test timeout message in multiple columns    FAIL
    Custom message should be deprecated with [Timeout] in tests    2    My test timeout message in multiple columns

Test Timeout Message With Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Test message from variable    FAIL
    Custom message should be deprecated with [Timeout] in tests    3    Test \${MESSAGE}

Keyword Timeout Message
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    My keyword timeout message    FAIL
    Custom message should be deprecated with [Timeout] in keywords    4    My keyword timeout message

Keyword Timeout Message In Multiple Columns
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    My keyword timeout message in multiple columns    FAIL
    Custom message should be deprecated with [Timeout] in keywords    5    My keyword timeout message in multiple columns

Keyword Timeout Message With Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Keyword message from variable    FAIL
    Custom message should be deprecated with [Timeout] in keywords    6    Keyword \${MESSAGE}

*** Keywords ***
Custom message should be deprecated with Test Timeout
    [Arguments]    ${index}    ${message}
    ${path} =    Normalize Path    ${DATADIR}/core/timeouts_with_custom_messages.robot
    ${warning} =    Catenate    Error in file '${path}':
    ...    ${DEPRECATED}
    ...    Message that was used is '${message}'.
    Check Log Message    @{ERRORS}[${index}]    ${warning}    WARN

Custom message should be deprecated with [Timeout] in tests
    [Arguments]    ${index}    ${message}
    ${path} =    Normalize Path    ${DATADIR}/core/timeouts_with_custom_messages.robot
    ${warning} =    Catenate    Error in file '${path}':
    ...    Invalid syntax in test case '${TEST NAME}':
    ...    ${DEPRECATED}
    ...    Message that was used is '${message}'.
    Check Log Message    @{ERRORS}[${index}]    ${warning}    WARN

Custom message should be deprecated with [Timeout] in keywords
    [Arguments]    ${index}    ${message}
    ${path} =    Normalize Path    ${DATADIR}/core/timeouts_with_custom_messages.robot
    ${warning} =    Catenate    Error in file '${path}':
    ...    Invalid syntax in keyword '${TEST NAME}':
    ...    ${DEPRECATED}
    ...    Message that was used is '${message}'.
    Check Log Message    @{ERRORS}[${index}]    ${warning}    WARN
