*** Settings ***

Test Teardown    Fail If Timeout Occurred


*** Test Cases ***

Run Keyword If Timeout Occurred When Test Timeout Occurred
    [Documentation]  FAIL Test timeout 1 second exceeded.\n\nAlso teardown failed:\nTimeout occurred!
    [Timeout]  1 second
    Sleep  2 seconds

Run Keyword If Timeout Occurred When Test Timeout Did Not Occur
    [Timeout]  1 second
    No Operation

Run Keyword If Timeout Occurred When Test Timeout Occurred In Setup
    [Documentation]  FAIL Setup failed:\nTest timeout 1 second exceeded.\n\nAlso teardown failed:\nTimeout occurred!
    [Timeout]  1 second
    [Setup]  Sleep  2 seconds
    No Operation

Run Keyword If Timeout Occurred When Test Timeout Did Not Occur In Setup
    [Timeout]  1 second
    [Setup]  No Operation
    No Operation

Run Keyword If Timeout Occurred When Keyword Timeout Occurred
    [Documentation]  FAIL Keyword timeout 1 second exceeded.\n\nAlso teardown failed:\nTimeout occurred in keyword!
    Keyword With Timeout Failing
    [Teardown]  Run Keyword If Timeout Occurred  Fail  Timeout occurred in keyword!

Run Keyword If Timeout Occurred When Keyword Timeout Did Not Occur
    Keyword With Timeout Passing

Run Keyword If Timeout Occurred When Keyword Timeout Occurred In Setup
    [Documentation]  FAIL Setup failed:\nKeyword timeout 1 second exceeded.\n\nAlso teardown failed:\nTimeout occurred!
    [Setup]  Keyword With Timeout Failing
    No Operation

Run Keyword If Timeout Occurred When Keyword Timeout Did Not Occur In Setup
    [Setup]  Keyword With Timeout Passing
    No Operation

Run Keyword If Timeout Occurred Used Outside Teardown
    [Documentation]  FAIL Keyword 'Run Keyword If Timeout Occurred' can only be used in test teardown
    Fail If Timeout Occurred

Run Keyword If Timeout Occurred Used When No Timeout Is Set
    No Operation

Returning Value From Run Keyword If Timeout Occurred
    [Documentation]  FAIL  Keyword timeout 1 second exceeded.
    Keyword With Timeout Failing
    [Teardown]  Return value from Run Keyword If Timeout Occurred


*** Keywords ***

Fail If Timeout Occurred
    Run Keyword If Timeout Occurred  Fail  Timeout occurred!

Keyword With Timeout Failing
    [Timeout]  1 seconds
    Sleep  2 seconds

Keyword With Timeout Passing
    [Timeout]  1 seconds
    No Operation

Return value from Run Keyword If Timeout Occurred
    ${value}  Run Keyword If Timeout Occurred  Set Variable  timeout
    Should Be Equal  ${value}  timeout

