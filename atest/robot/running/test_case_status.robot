*** Setting ***
Documentation     Tests for setting test case status correctly when test passes
...               and when a failure or error occurs. Also includes test cases
...               for running test setup and teardown in different situations.
Suite Setup       Run Tests    ${EMPTY}    running/test_case_status.robot
Resource          atest_resource.robot

*** Test Case ***
Test Passes
    Check Test Case    Test Pass

Test Fails
    Check Test Case    Test Fail

Non-Existing Keyword Error
    Check Test Case    Non-Existing Keyword Error

Test Setup Passes
    Check Test Case    Tests Setup Pass

Test Setup Fails
    [Documentation]    Checks also that test is not run if setup fails
    Check Test Case    Tests Setup Fail

Test Setup Errors
    Check Test Case    Tests Setup Error Non Existing KW

Test Teardown Passes
    Check Test Case    Tests Teardown Pass

Test Teardown Fails
    Check Test Case    Tests Teardown Fail

Test Teardown Errors
    Check Test Case    Tests Teardown Error Non Existing KW

Test And Teardown Fails
    Check Test Case    Test And Teardown Fails

Test Setup And Teardown Pass
    Check Test Case    Test Setup And Teardown Pass

Test Teardown is Run When Setup Fails
    ${test}    Check Test Case    Test Teardown is Run When Setup Fails
    ${td} =    Set Variable    ${test.teardown}
    Should Not Be Equal    ${td}    ${None}    Teardown not run    No values
    Length Should Be   ${td.msgs}    1
    Check Log Message    ${td.msgs[0]}    Hello from teardown!
    Length Should Be   ${td.kws}    0

Test Setup And Teardown Fails
    Check Test Case    Test Setup And Teardown Fails
