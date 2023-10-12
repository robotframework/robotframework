*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    test_libraries/timestamps_for_stdout_messages.robot
Resource        atest_resource.robot

*** Test Cases ***
Library adds timestamp as integer
    Test's timestamps should be correct    931000

Library adds timestamp as float
    Test's timestamps should be correct    930502

*** Keywords ***
Test's timestamps should be correct
    [Arguments]    ${micro}
    ${tc} =    Check Test Case    ${TESTNAME}
    Known timestamp should be correct    ${tc.body[0].msgs[0]}    ${micro}
    Current timestamp should be smaller than kw end time    ${tc.body[0]}

Known timestamp should be correct
    [Arguments]    ${msg}    ${micro}
    Check Log Message    ${msg}    Known timestamp
    Should Be Equal    ${msg.timestamp}    ${datetime(2011, 6, 18, 20, 43, 54, ${micro})}

Current timestamp should be smaller than kw end time
    [Arguments]    ${kw}
    Check Log Message    ${kw.msgs[1]}    <b>Current</b>    INFO    html=True
    Should Be True    $kw.end_time > $kw.msgs[1].timestamp
