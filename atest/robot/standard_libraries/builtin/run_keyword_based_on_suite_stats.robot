*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_based_on_suite_stats
Resource          atest_resource.robot

*** Test Cases ***
Run Keyword If All Tests Passed
    ${suite} =    Get Test Suite    Run Keyword If All Tests Passed When All Pass
    Should Be Equal As Integers    ${suite.statistics.failed}    0
    Should Be Equal    ${suite.teardown.kws[0].name}    My Teardown
    Check Log Message    ${suite.teardown.kws[0].kws[0].msgs[0]}    Suite teardown message

Run Keyword If All Tests Passed Can't be Used In Test
    Check Test Case    Run Keyword If All Tests Passed Can't be Used In Test

Run Keyword If All tests Passed Is not Executed When Any Test Fails
    Check Test Case    Run Keyword If All tests Passed Is not Executed When Any Test Fails

Run Keyword If Any Tests Failed
    ${suite} =    Get Test Suite    Run Keyword If Any Tests Failed When Test Fails
    Should Be Equal As Integers    ${suite.statistics.failed}    1
    Should Be Equal    ${suite.teardown.kws[0].name}    My Teardown
    Check Log Message    ${suite.teardown.kws[0].kws[0].msgs[0]}    Suite teardown message

Run Keyword If Any Tests Failed Can't be Used In Test
    Check Test Case    Run Keyword If Any Tests Failed Can't be Used In Test

Run Keyword If Any Tests failed Is not executed when All Tests Pass
    Check Test Case    Run Keyword If Any Tests failed Is not executed when All Tests Pass
