*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    tags/-tag_syntax.robot
Resource          atest_resource.robot

*** Test Cases ***
Remove from test
    Check Test Tags   ${TEST NAME}    tag1    tag3    tag4

Remove from test using pattern
    Check Test Tags   ${TEST NAME}    -in-settings    tag    tag3

Remove from keyword
    ${tc} =    Check Test Case    Remove from test
    Check Keyword Data    ${tc.kws[0]}    ${TEST NAME}    tags=-in-settings, kw2

Remove from keyword using pattern
    ${tc} =    Check Test Case    Remove from test using pattern
    Check Keyword Data    ${tc.kws[0]}    -tag_syntax.${TEST NAME}    tags=r1, r5, r6

Escaped
    Check Test Tags    ${TESTNAME}    -escaped    -in-settings    tag    tag1    tag2    tag3

Variable
    Check Test Tags    ${TESTNAME}    -in-settings    -variable    tag    tag1    tag2    tag3
