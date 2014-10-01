*** Settings ***
Resource        atest_resource.robot


***Keywords***

Library import should have been successful
    [Arguments]  ${lib}  @{params}
    Check Test Case  ${TEST NAME}
    ${par} =  Catenate  SEPARATOR=${SPACE}|${SPACE}  @{params}
    Check Syslog Contains  Imported library '${lib}' with arguments [ ${par} ]

Library import should have failed
    [Arguments]  ${lib}  ${err}
    Check Syslog Contains  Test Library '${lib}' expected ${err}
