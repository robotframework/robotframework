*** Settings ***
Force Tags        force1    force2
Suite Setup       Pass Execution In Keyword    tag1    tag2    -*2
Suite Teardown    Pass Execution In Keyword

*** Test Cases ***
Test in suite with valid Pass Execution usage in Suite Setup and Teardown
    [Documentation]    FAIL Test is run normally.
    Fail    Test is run normally.

*** Keywords ***
Pass Execution In Keyword
    [Arguments]    @{tags}
    Pass Execution    message    @{tags}
    Fail    Not executed
