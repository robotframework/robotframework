*** Settings ***
Documentation     Merge test cases for test doc HTML formatting

*** Variables ***
${USE_HTML}       ${false}
${TEXT MESSAGE}   Test message
${HTML MESSAGE}   *HTML* <b>Test</b> message

*** Test Cases ***
Html1
    Set Test Documentation   FAIL ${TEXT MESSAGE}
    Fail    ${TEXT MESSAGE}

Html2
    ${msg}  Set Variable If  ${USE_HTML}   ${HTML MESSAGE}   ${TEXT MESSAGE}
    Set Test Documentation   FAIL ${msg}
    Fail    ${msg}

Html3
    Set Test Documentation   FAIL ${HTML MESSAGE}
    Fail    ${HTML MESSAGE}

Html4
    ${msg}  Set Variable If  not ${USE_HTML}   ${HTML MESSAGE}   ${TEXT MESSAGE}
    Set Test Documentation   FAIL ${msg}
    Fail    ${msg}
