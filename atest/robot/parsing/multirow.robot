*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  parsing/multirow.robot
Resource        atest_resource.robot

*** Test Cases ***
Multirow Settings
    Should Be Equal  ${SUITE.doc}  NO RIDE!! This doc is one long string\n!\n!\n!\n!
    Should Contain Tags   ${SUITE.tests[0]}  ...  t1  t2  t3  t4  t5  t6  t7  t8  t9

Multirow Variables
    Check Test Case  ${TEST NAME}

Multirow Import
    Check Test Case  ${TEST NAME}

Multirow Args For Library Keyword
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  one
    Check Log Message  ${tc.kws[0].msgs[1]}  two
    Check Log Message  ${tc.kws[0].msgs[2]}  three
    Check Log Message  ${tc.kws[0].msgs[3]}  four
    Check Log Message  ${tc.kws[0].msgs[4]}  five

Multirow Args For User Keyword
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  1
    Check Log Message  ${tc.kws[0].kws[0].msgs[1]}  2
    Check Log Message  ${tc.kws[0].kws[0].msgs[2]}  3
    Check Log Message  ${tc.kws[0].kws[0].msgs[3]}  4
    Check Log Message  ${tc.kws[0].kws[0].msgs[4]}  5

Multirow In User Keyword
    Check Test Case  ${TEST NAME}

Multirow Return Values
    Check Test Case  ${TEST NAME}

Multirow Test Settings
    ${tc} =  Check Test Case  ${TEST NAME}
    @{expected}=   Evaluate  ['my'+str(i) for i in range(1,6)]
    Should Contain Tags   ${tc}  @{expected}
    Should Be Equal  ${tc.doc}  This test doc is one \nlong string

Multirow User Keyword Settings
    Check Test Case  ${TEST NAME}

Multirow With For Loop Declaration
    Check Test Case  ${TEST NAME}

Multirow With For Loop Keywords
    Check Test Case  ${TEST NAME}

Invalid Multirow Usage
    Check Multirow Error From Stderr  Non-existing setting '...'.
    Check Multirow Error From Stderr  Setting variable '...' failed: Invalid variable name '...'.
    Check Test Case  \
    Check Test Case  Invalid Usage In Test And User Keyword

*** Keywords ***
Check Multirow Error From Stderr
    [Arguments]  ${err}
    ${path} =  Join Path  ${CURDIR}  ..  ..  testdata  parsing  multirow.robot
    Check Stderr Contains  [ ERROR ] Error in file '${path}': ${err}
