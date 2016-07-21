*** Settings ***
Documentation   Tests for customizing timeout messages. Main timeout functionality is tested in Timeouts and also in Metadata. It seems that on Cygwin Python tests now and then fail with an error message "error: can't allocate lock"
Suite Setup     Run Tests  ${EMPTY}  core${/}timeouts_with_custom_messages.robot
Resource        atest_resource.robot

*** Test Cases ***
Default Test Timeout Message
    ${test} =  Check Test Case  Default Test Timeout Message
    Check Log Message  ${test.kws[0].msgs[0]}  My customized default test timeout  FAIL

Test Timeout Message
    ${test} =  Check Test Case  Test Timeout Message
    Check Log Message  ${test.kws[0].msgs[0]}  My test timeout message  FAIL

Test Timeout Message In Multiple Columns
    ${test} =  Check Test Case  Test Timeout Message In Multiple Columns
    Check Log Message  ${test.kws[0].msgs[0]}  My test timeout message in multiple columns  FAIL

Test Timeout Message With Variables
    ${test} =  Check Test Case  Test Timeout Message With Variables
    Check Log Message  ${test.kws[0].msgs[0]}  Test message from variable  FAIL

Keyword Timeout Message
    ${test} =  Check Test Case  Keyword Timeout Message
    Check Log Message  ${test.kws[1].kws[0].msgs[0]}  My keyword timeout message  FAIL

Keyword Timeout Message In Multiple Columns
    ${test} =  Check Test Case  Keyword Timeout Message In Multiple Columns
    Check Log Message  ${test.kws[0].kws[0].msgs[0]}  My keyword timeout message in multiple columns  FAIL

Keyword Timeout Message With Variables
    ${test} =  Check Test Case  Keyword Timeout Message With Variables
    Check Log Message  ${test.kws[0].kws[0].msgs[0]}  Keyword message from variable  FAIL

