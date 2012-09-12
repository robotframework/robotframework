*** Settings ***
Library          OperatingSystem
Test Teardown    Remove File    ${VARFILE}

*** Variables ***
${VARFILE}    %{TEMPDIR}/robot_variable_test.py

*** Test Cases ***

Importing Same Variable File Does Not Re-Import Module
    Test Import    initial value
    Sleep    1 second    Make sure py and pyc files get different timestamps
    Test Import    new value

*** Keywords ***

Test Import
    [Arguments]    ${value}
    Create File    ${VARFILE}    VAR = '${value}'
    Import Variables    ${VARFILE}
    Should Be Equal    ${VAR}    initial value

