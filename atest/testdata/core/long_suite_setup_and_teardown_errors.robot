*** Settings ***
Suite Setup       Long Error    setup
Suite Teardown    Long Error    teardown

*** Variables ***
${CUT}            \\[ Message content over the limit has been removed\\. \\]

*** Test Cases ***
Test
    [Documentation]    FAIL REGEXP:
    ...    Parent suite setup failed:
    ...    (setup\\n){20} {4}${CUT}\\n(setup\\n){20}
    ...    Also parent suite teardown failed:
    ...    (teardown\\n){20} {4}${CUT}\\n(teardown\\n){19}teardown
    No Operation

*** Keywords ***
Long Error
    [Arguments]    ${where}
    ${error} =    Evaluate    '${where}\\n' * 100
    Fail    ${error}
