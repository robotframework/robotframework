*** Settings ***
Force Tags        pybot    jybot    regression
Suite Teardown    Remove File    ${LOG}
Resource          ./modifier_resource.robot

*** Test Cases ***
Modifier as path
    Run Tests    --prerebotmodifier ${CURDIR}/ModelModifier.py -l ${LOG}   ${TEST DATA}
    Output should not be modified
    Log should be modified    visited

Modifier as name
    Run Tests    --prerebotmodifier ModelModifier --pythonpath ${CURDIR} -l ${LOG}    ${TEST DATA}
    Output should not be modified
    Log should be modified    visited

Modifier with arguments separated with ':'
    Run Tests    --PreRebotModifier ${CURDIR}/ModelModifier.py:new:tags -l ${LOG}    ${TEST DATA}
    Output should not be modified
    Log should be modified    new    tags

Modifier with arguments separated with ';'
    Run Tests    --prerebot "ModelModifier;a4aas019" --prere "ModelModifier;sa10aaga3" -P ${CURDIR} -l ${LOG}    ${TEST DATA}
    Output should not be modified
    Log should be modified    a4aas019    sa10aaga3

Pre-run and pre-rebot modifiers together
    Run Tests    --prerun ModelModifier:pre-run --prerebot ModelModifier:pre-rebot -P ${CURDIR} -l ${LOG}    ${TEST DATA}
    Output should be modified    pre-run
    Log should be modified    pre-run    pre-rebot

Non-existing modifier
    Run Tests    --prerebotmodifier NobodyHere -l ${LOG}    ${TEST DATA}
    Stderr Should Match
    ...    [ ERROR ] Importing model modifier 'NobodyHere' failed: ImportError:
    ...    No module named NobodyHere\nTraceback (most recent call last):\n*
    Output should not be modified
    Log should not be modified

Invalid modifier
    Run Tests    --prerebotmodifier ${CURDIR}/ModelModifier.py:FAIL:Message -l ${LOG}    ${TEST DATA}
    Stderr Should Match
    ...    [ ERROR ] Executing model modifier 'ModelModifier' failed:
    ...    Message\nTraceback (most recent call last):\n*
    Output should not be modified
    Log should not be modified
