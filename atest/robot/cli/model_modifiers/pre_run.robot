*** Settings ***
Resource           modifier_resource.robot

*** Test Cases ***
Modifier as path
    Run Tests    --prerunmodifier ${CURDIR}/ModelModifier.py -l ${LOG}   ${TEST DATA}
    Output should be modified    visited
    Log should be modified    visited

Modifier as name
    Run Tests    --prerunmodifier ModelModifier --pythonpath ${CURDIR} -l ${LOG}    ${TEST DATA}
    Output should be modified    visited
    Log should be modified    visited

Modifier with arguments separated with ':'
    Run Tests    --PreRunModifier ${CURDIR}/ModelModifier.py:new:tags -l ${LOG}    ${TEST DATA}
    Output should be modified    new    tags
    Log should be modified    new    tags

Modifier with arguments separated with ';'
    Run Tests    --prerun "ModelModifier;1;2;3" --preru "ModelModifier;4;5" -P ${CURDIR} -l ${LOG}    ${TEST DATA}
    Output should be modified    1    2    3    4    5
    Log should be modified    1    2    3    4    5

Non-existing modifier
    Run Tests    --prerunmodifier NobodyHere -l ${LOG}   ${TEST DATA}
    ${quote} =    Set Variable If    ${INTERPRETER.is_py3}    '    ${EMPTY}
    Stderr Should Match
    ...    ? ERROR ? Importing model modifier 'NobodyHere' failed: *Error:
    ...    No module named ${quote}NobodyHere${quote}\nTraceback (most recent call last):\n*
    Output should not be modified
    Log should not be modified

Invalid modifier
    Run Tests    --prerunmodifier ${CURDIR}/ModelModifier.py:FAIL:Message -l ${LOG}    ${TEST DATA}
    Stderr Should Start With
    ...    [ ERROR ] Executing model modifier 'ModelModifier' failed:
    ...    Message\nTraceback (most recent call last):\n
    Output should not be modified
    Log should not be modified

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

Modifiers are used after normal configuration
    ${result} =    Run Tests Without Processing Output
    ...    --include nonex --name Custom --prerun ${CURDIR}/ModelModifier.py:REMOVE:ALL:TESTS    ${TEST DATA}
    Stderr Should Be Equal To
    ...    [ ERROR ] Suite 'Custom' contains no tests matching tag 'nonex'.${USAGE TIP}\n
    Should Be Equal    ${result.rc}    ${252}
