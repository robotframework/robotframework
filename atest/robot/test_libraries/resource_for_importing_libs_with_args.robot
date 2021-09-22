*** Settings ***
Resource        atest_resource.robot

***Keywords***
Library import should have been successful
    [Arguments]    ${lib}    @{params}
    Check Test Case  ${TEST NAME}
    ${par} =    Catenate    SEPARATOR=${SPACE}|${SPACE}    @{params}
    Syslog Should Contain    Imported library '${lib}' with arguments [ ${par} ]

Library import should have failed
    [Arguments]    ${lib}    ${err}
    Syslog Should Contain    Library '${lib}' expected ${err}
