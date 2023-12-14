*** Settings ***
Resource          atest_resource.robot

*** Variables ***
${SOURCE}         output/listener_interface/body_items_v3/tests.robot
${MODIFIER}       output/listener_interface/body_items_v3/DataModifier.py
@{ALL TESTS}      Library keyword    User keyword    IF    TRY    FOR    WHILE    VAR
...               Non-existing keyword    Empty keyword    Duplicate keyword
...               Invalid keyword    Invalid syntax    Run Keyword

*** Test Cases ***
Validate that all methods are called correctly
    Run Tests    ${EMPTY}    ${SOURCE}
    Should contain tests    ${SUITE}    @{ALL TESTS}
    Check Log Message    ${SUITE.teardown.messages[0]}    Listener StartEndBobyItemOnly is OK.
    Check Log Message    ${SUITE.teardown.messages[1]}    Listener SeparateMethods is OK.
    Check Log Message    ${SUITE.teardown.messages[2]}    Listener SeparateMethodsAlsoForKeywords is OK.

Data and results can be modified
    Run Tests    --variable VALIDATE_EVENTS:False --listener ${DATADIR}/${MODIFIER}    ${SOURCE}
    Should contain tests    ${SUITE}    @{ALL TESTS}
    ...    Library keyword=FAIL:state: set by listener
    ...    User keyword=FAIL:Failed by listener once!
    ...    Empty keyword=PASS
    ...    Non-existing keyword=PASS
    ...    Duplicate keyword=PASS
    ...    Invalid keyword=PASS
    ...    FOR=FAIL:Listener failed me at 'b'!
    ...    WHILE=FAIL:Fail at iteration 10.
