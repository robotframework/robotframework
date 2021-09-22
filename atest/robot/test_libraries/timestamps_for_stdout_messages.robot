*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/timestamps_for_stdout_messages.robot
Resource        atest_resource.robot

*** Test Cases ***
Library adds timestamp as integer
    Test's timestamps should be correct

Library adds timestamp as float
    Test's timestamps should be correct

*** Keywords ***
Test's timestamps should be correct
    ${tc} =  Check Test Case  ${TESTNAME}
    Known timestamp should be correct  ${tc.kws[0].msgs[0]}
    Current timestamp should be smaller than kw end time  ${tc.kws[0]}

Known timestamp should be correct
    [Arguments]  ${msg}
    Check log message  ${msg}  Known timestamp
    Should Be Equal  ${msg.timestamp}  20110618 20:43:54.931

Current timestamp should be smaller than kw end time
    [Arguments]  ${kw}
    Check log message  ${kw.msgs[1]}  <b>Current</b>  INFO  html=True
    Should Be True  "${kw.endtime}" > "${kw.msgs[1].timestamp}"
