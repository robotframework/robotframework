*** Settings ***
Suite Setup        Suite Setup
Suite Teardown     Suite Teardown

*** Test Cases ***
Set Test Variable cannot be used in suite setup or teardown
    [Documentation]    FAIL
    ...    Parent suite teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Cannot set test variable when no test is started.
    ...
    ...    2) Cannot set test variable when no test is started.
    No Operation

*** Keywords ***
Suite Setup
    TRY
        Set Test Variable    ${VAR}    Fails!
    EXCEPT    Cannot set test variable when no test is started.
        No Operation
    ELSE
        Fail    Should have failed!
    END

Suite Teardown
    Set Test Variable    ${VAR}    Fails!
    Set Test Variable    ${VAR}    Fails again!
