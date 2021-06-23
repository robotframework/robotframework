*** Settings ***
Suite Setup     Check Suite Source  ${EXPECTED SUITE SOURCE}
Suite Teardown  Check Suite Source  ${EXPECTED SUITE SOURCE}
Test Setup      Check Suite Source  ${EXPECTED SUITE SOURCE}
Test Teardown   Check Suite Source  ${EXPECTED SUITE SOURCE}
Resource        resource.robot

*** Variables ***
${EXPECTED SUITE SOURCE}  ${CURDIR}${/}suite_source_in_file_suite.robot

*** Test Cases ***
\${SUITE SOURCE} in file suite
    Should Be Equal  ${SUITE SOURCE}  ${EXPECTED SUITE SOURCE}

\${SUITE SOURCE} in user keyword
    Check Suite Source  ${EXPECTED SUITE SOURCE}

\${SUITE SOURCE} in resource file
    Check Suite Source In Resource File  ${EXPECTED SUITE SOURCE}

*** Keywords ***
Check Suite Source
    [Arguments]  ${expected suite source}
    Should Be Equal  ${SUITE SOURCE}  ${expected suite source}

