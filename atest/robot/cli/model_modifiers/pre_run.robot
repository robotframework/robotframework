*** Settings ***
Resource           modifier_resource.robot

*** Test Cases ***
Modifier as path
    Run Tests    --prerunmodifier ${CURDIR}/ModelModifier.py -l ${LOG}   ${TEST DATA}
    Output and log should be modified    visited

Modifier as name
    Run Tests    --prerunmodifier ModelModifier --pythonpath ${CURDIR} -l ${LOG}    ${TEST DATA}
    Output and log should be modified    visited

Modifier with arguments separated with ':'
    Run Tests    --PreRunModifier ${CURDIR}/ModelModifier.py:new:tags:named=tag -l ${LOG}    ${TEST DATA}
    Output and log should be modified    new    tags    named-tag

Modifier with arguments separated with ';'
    Run Tests    --prerun "ModelModifier;1;2;3" --preru "ModelModifier;4;5;n=t" -P ${CURDIR} -l ${LOG}    ${TEST DATA}
    Output and log should be modified    1    2    3    4    5    n-t

Non-existing modifier
    Run Tests    --prerunmodifier NobodyHere -l ${LOG}   ${TEST DATA}
    Stderr Should Match
    ...    ? ERROR ? Importing model modifier 'NobodyHere' failed: *Error:
    ...    No module named 'NobodyHere'\nTraceback (most recent call last):\n*
    Output and log should not be modified

Invalid modifier
    Run Tests    --prerunmodifier ${CURDIR}/ModelModifier.py:FAIL:Message -l ${LOG}    ${TEST DATA}
    Stderr Should Start With
    ...    [ ERROR ] Executing model modifier 'ModelModifier' failed:
    ...    Message\nTraceback (most recent call last):\n
    Output and log should not be modified

Error if all tests removed
    ${result} =    Run Tests Without Processing Output
    ...    --prerun ${CURDIR}/ModelModifier.py:REMOVE:ALL:TESTS    ${TEST DATA}
    Stderr Should Be Equal To
    ...    [ ERROR ] Suite 'Pass And Fail' contains no tests after model modifiers.${USAGE TIP}\n
    Should Be Equal    ${result.rc}    ${252}

--RunEmptySuite when all tests removed
    Run Tests    --RunEmptySuite --PreRun ${CURDIR}/ModelModifier.py:REMOVE:ALL:TESTS    ${TEST DATA}
    Stderr Should Be Empty
    Length Should Be    ${SUITE.tests}    0

Modifiers are used before normal configuration
    ${result} =    Run Tests
    ...    --include added --prerun ${CURDIR}/ModelModifier.py:CREATE:name=Created:tags=added    ${TEST DATA}
    Stderr Should Be Empty
    Length Should Be    ${SUITE.tests}    1
    ${tc} =    Check test case    Created    FAIL    Test case contains no keywords.
    Lists should be equal    ${tc.tags}    ${{['added']}}

Modify FOR and IF
    Run Tests    --prerun ${CURDIR}/ModelModifier.py    misc/for_loops.robot misc/if_else.robot
    ${tc} =    Check Test Case    For In Range Loop In Test
    Check Log Message    ${tc.body[0].body[0].body[0].msgs[0]}   FOR
    Check Log Message    ${tc.body[0].body[1].body[0].msgs[0]}   is
    Check Log Message    ${tc.body[0].body[2].body[0].msgs[0]}   modified!
    ${tc} =    Check Test Case    If structure
    Check Log Message    ${tc.body[0].body[0].body[0].msgs[0]}   going here!
