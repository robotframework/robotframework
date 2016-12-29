*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    core/timeouts_with_custom_messages.robot
Resource          atest_resource.robot

*** Test Cases ***
Default Test Timeout Message
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    My customized default test timeout    FAIL

Test Timeout Message
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    My test timeout message    FAIL

Test Timeout Message In Multiple Columns
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    My test timeout message in multiple columns    FAIL

Test Timeout Message With Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Test message from variable    FAIL

Keyword Timeout Message
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    My keyword timeout message    FAIL

Keyword Timeout Message In Multiple Columns
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    My keyword timeout message in multiple columns    FAIL

Keyword Timeout Message With Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Keyword message from variable    FAIL
