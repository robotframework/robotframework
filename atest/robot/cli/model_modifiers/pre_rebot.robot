*** Settings ***
Force Tags        pybot    jybot    regression
Suite Setup       Create Output With Robot    ${MODIFIED OUTPUT}    ${EMPTY}    ${TEST DATA}
Suite Teardown    Remove File    ${MODIFIED OUTPUT}
Resource          modifier_resource.robot
Resource          rebot_resource.robot

*** Variables ***
${MODIFIED OUTPUT}    %{TEMPDIR}/pre_rebot_modified.xml

*** Test Cases ***
Modifier as path
    Run Rebot    --prerebotmodifier ${CURDIR}/ModelModifier.py -l ${LOG}    ${MODIFIED OUTPUT}
    Output should be modified    visited
    Log should be modified    visited

Modifier as name
    Run Rebot    --prerebotmodifier ModelModifier --pythonpath ${CURDIR} -l ${LOG}    ${MODIFIED OUTPUT}
    Output should be modified    visited
    Log should be modified    visited

Modifier with arguments separated with ':'
    Run Rebot    --PreRebotModifier ${CURDIR}/ModelModifier.py:new:tags -l ${LOG}    ${MODIFIED OUTPUT}
    Check Test Tags    Pass    force    new    pass    tags
    Output should be modified    new    tags
    Log should be modified    new    tags

Modifier with arguments separated with ';'
    Run Rebot    --prerebot "ModelModifier;1;2;3" --prere "ModelModifier;4;5" -P ${CURDIR} -l ${LOG}    ${MODIFIED OUTPUT}
    Output should be modified    1    2    3    4    5
    Log should be modified    1    2    3    4    5

Non-existing modifier
    Run Rebot    --prerebotmod NobodyHere -l ${LOG}    ${MODIFIED OUTPUT}
    Stderr Should Match
    ...    [ ERROR ] Importing model modifier 'NobodyHere' failed: ImportError:
    ...    No module named NobodyHere\nTraceback (most recent call last):\n*
    Output should not be modified
    Log should not be modified

Invalid modifier
    Run Rebot    --prerebotmodifier ${CURDIR}/ModelModifier.py:FAIL:Message -l ${LOG}    ${MODIFIED OUTPUT}
    Stderr Should Match
    ...    [ ERROR ] Executing model modifier 'ModelModifier' failed:
    ...    Message\nTraceback (most recent call last):\n*
    Output should not be modified
    Log should not be modified
