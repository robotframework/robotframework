*** Setting ***
Documentation     Tests for setting test case status correctly when test passes and when a failure or error occurs. Also includes test cases for running test setup and teardown in different situations.
Suite Setup       Run Tests    ${EMPTY}    core/test_case_status.robot
Resource          atest_resource.robot

*** Variable ***

*** Test Case ***
Test Passes
    Check Testcase    Test Pass

Test Fails
    Check Testcase    Test Fail

Non-Existing Keyword Error
    Check Testcase    Non-Existing Keyword Error

Test Setup Passes
    Check Testcase    Tests Setup Pass

Test Setup Fails
    [Documentation]    Checks also that test is not run if setup fails
    Check Testcase    Tests Setup Fail

Test Setup Errors
    Check Testcase    Tests Setup Error Non Existing KW

Test Teardown Passes
    Check Testcase    Tests Teardown Pass

Test Teardown Fails
    Check Testcase    Tests Teardown Fail

Test Teardown Errors
    Check Testcase    Tests Teardown Error Non Existing KW

Test And Teardown Fails
    Check Testcase    Test And Teardown Fails

Test Setup And Teardown Pass
    Check Testcase    Test Setup And Teardown Pass

Test Teardown is Run When Setup Fails
    ${test}    Check Testcase    Test Teardown is Run When Setup Fails
    ${td} =    Set Variable    ${test.teardown}
    Should Not Be Equal    ${td}    ${None}    Teardown not run    No values
    Length Should Be   ${td.msgs}    1
    Check Log Message    ${td.msgs[0]}    Hello from teardown!
    Length Should Be   ${td.kws}    0

Test Setup And Teardown Fails
    Check Testcase    Test Setup And Teardown Fails
