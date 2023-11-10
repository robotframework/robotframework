*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/return.robot
Resource          atest_resource.robot

*** Test Cases ***
Simple
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].body[1].type}      RETURN
    Should Be Equal    ${tc.body[0].body[1].values}    ${{()}}
    Should Be Equal    ${tc.body[0].body[1].status}    PASS
    Should Be Equal    ${tc.body[0].body[1].message}   ${EMPTY}
    Should Be Equal    ${tc.body[0].body[2].status}    NOT RUN
    Should Be Equal    ${tc.body[0].message}           ${EMPTY}

Return value
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].body[0].type}      RETURN
    Should Be Equal    ${tc.body[0].body[0].values}    ${{('value',)}}

Return value as variable
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].body[0].type}      RETURN
    Should Be Equal    ${tc.body[0].body[0].values}    ${{('\${42}',)}}

Return multiple values
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].body[0].type}      RETURN
    Should Be Equal    ${tc.body[0].body[0].values}    ${{('first', '\${2}', 'third')}}

In nested keyword
    Check Test Case    ${TESTNAME}

In IF
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].body[0].body[0].body[0].type}      RETURN
    Should Be Equal    ${tc.body[0].body[0].body[0].body[0].status}    PASS
    Should Be Equal    ${tc.body[0].body[0].body[0].body[1].status}    NOT RUN
    Should Be Equal    ${tc.body[0].body[1].status}                    NOT RUN
    Should Be Equal    ${tc.body[2].body[0].body[1].body[0].type}      RETURN
    Should Be Equal    ${tc.body[2].body[0].body[1].body[0].status}    PASS
    Should Be Equal    ${tc.body[2].body[0].body[1].body[1].status}    NOT RUN
    Should Be Equal    ${tc.body[2].body[1].status}                    NOT RUN

In inline IF
    Check Test Case    ${TESTNAME}

In FOR
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].body[0].body[0].body[0].type}      RETURN
    Should Be Equal    ${tc.body[0].body[0].body[0].body[0].status}    PASS
    Should Be Equal    ${tc.body[0].body[0].body[0].body[1].status}    NOT RUN
    Should Be Equal    ${tc.body[0].body[1].status}                    NOT RUN

In nested FOR/IF structure
    Check Test Case    ${TESTNAME}

In test
    Check Test Case    ${TESTNAME}

In test with values
    Check Test Case    ${TESTNAME}

In test inside IF
    Check Test Case    ${TESTNAME}

In test inside FOR
    Check Test Case    ${TESTNAME}

In test inside WHILE
    Check Test Case    ${TESTNAME}

In test inside TRY
    Check Test Case    ${TESTNAME}
