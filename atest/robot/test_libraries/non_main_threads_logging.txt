*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/non_main_threads_logging.txt
Force Tags      regression  pybot  jybot
Resource        atest_resource.txt

*** Test Cases ***

Log messages from non-main threads should be ignored
    ${tc} =  Check Test Case  ${TESTNAME}
    Should Be Empty      ${tc.kws[0].msgs}
    Should Be Empty      ${tc.kws[1].msgs}
    Check Log Message    ${tc.kws[2].msgs[0]}      0
    Check Log Message    ${tc.kws[2].msgs[99]}    99
    Length Should Be     ${tc.kws[3].msgs}       100
    Check Log Message    ${tc.kws[3].msgs[0]}      0
    Check Log Message    ${tc.kws[3].msgs[99]}    99
    Length Should Be     ${tc.kws[3].msgs}       100
