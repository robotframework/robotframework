*** Setting ***
Documentation     Tests for setting test case status correctly when test passes and when a failure or error occurs. Also includes test cases for running test setup and teardown in different situations.
Suite Setup       Run Tests    ${EMPTY}    core/test_case_status.txt
Force Tags        regression    jybot    pybot
Resource          atest_resource.txt

*** Variable ***

*** Test Case ***
Test Passes
    Check Testcase    Test Pass

Test Fails
    Check Testcase    Test Fail

Test Errors
    Check Testcase    Test Error
    Check Testcase    Test Error Non Existing KW

Test Setup Passes
    Check Testcase    Tests Setup Pass

Test Setup Fails
    [Documentation]    Checks also that test is not run if setup fails
    Check Testcase    Tests Setup Fail

Test Setup Errors
    Check Testcase    Tests Setup Error
    Check Testcase    Tests Setup Error Non Existing KW

Test Teardown Passes
    Check Testcase    Tests Teardown Pass

Test Teardown Fails
    Check Testcase    Tests Teardown Fail

Test Teardown Errors
    Check Testcase    Tests Teardown Error
    Check Testcase    Tests Teardown Error Non Existing KW

Test And Teardown Fails
    Check Testcase    Test And Teardown Fails

Test Setup And Teardown Pass
    Check Testcase    Test Setup And Teardown Pass

Test Teardown is Run When Setup Fails
    ${test}    Check Testcase    Test Teardown is Run When Setup Fails
    ${td} =    Set    ${test.teardown}
    Fail If Equal    ${td}    ${None}    Teardown not run    No values
    Ints Equal    ${td.message_count}    1
    Check Log Message    ${td.messages[0]}    Hello from teardown!
    Ints Equal    ${td.keyword_count}    0

Test Setup And Teardown Fails
    Check Testcase    Test Setup And Teardown Fails
