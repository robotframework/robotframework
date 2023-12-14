*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    output/listener_interface/body_items_v3/tests.robot
Resource          atest_resource.robot

*** Variables ***
@{ALL TESTS}      Library keyword    User keyword    IF    TRY    FOR    WHILE    VAR
...               Non-existing keyword    Empty keyword    Duplicate keyword
...               Invalid keyword    Invalid syntax

*** Test Cases ***
All methods are called correctly
    Should contain tests    ${SUITE}    @{ALL TESTS}
    Check Log Message    ${SUITE.teardown.messages[0]}    All methods called correctly.
