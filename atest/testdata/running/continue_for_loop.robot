*** Settings ***
Library    JavaExceptions

*** Test Cases ***
Simple Continue For Loop
    :FOR    ${var}    IN    one    two
    \    Continue For Loop
    \    Fail    Should not be executed
    Should Be Equal    ${var}    two

Continue For Loop In `Run Keyword`
    ${text}=   Set Variable  ${EMPTY}
    :FOR    ${var}    IN    one    two    three
    \    Run Keyword If    '${var}' == 'two'    Continue For Loop
    \    ${text}=   Set Variable   ${text}${var}
    Should Be Equal    ${text}     onethree

Continue For Loop In User Keyword
    :FOR    ${var}    IN    one    two
    \    With Only Continue For Loop
    \    Fail    Should not be executed
    Should BE Equal    ${var}    two

Continue For Loop Should Terminate Immediate Loop Only
    :FOR    ${var}    IN    one    two
    \    With Loop
    \    ${x} =    Set Variable    ${var}-extra
    Should Be Equal    ${x}    two-extra

Continue For Loop In User Keyword Should Terminate Immediate Loop Only
    :FOR    ${var}    IN    one    two
    \    With Loop Within Loop
    \    ${x} =    Set Variable    ${var}-extra
    Should Be Equal    ${x}    two-extra

Continue For Loop In User Keyword Calling User Keyword With Continue For Loop
    :FOR    ${var}    IN    one    two
    \    With Keyword For Loop Calling Keyword With Continue For Loop
    \    ${x} =    Set Variable    ${var}-extra
    Should Be Equal    ${x}    two-extra

Continue For Loop Without For Loop Should Fail
   [Documentation]    FAIL Invalid 'Continue For Loop' usage.
   Continue For Loop

Continue For Loop In User Keyword Without For Loop Should Fail
   [Documentation]    FAIL Invalid 'Continue For Loop' usage.
   With Only Continue For Loop

Continue For Loop In Test Teardown
    No Operation
    [Teardown]      With Loop

Continue For Loop In Keyword Teardown
    Continue For Loop In Keyword Teardown

Invalid Continue For Loop In User Keyword Teardown
    [Documentation]    FAIL Keyword teardown failed:
    ...                Invalid 'Continue For Loop' usage.
    :FOR    ${var}    IN    one   two
    \     Invalid Continue For Loop In User Keyword Teardown

Continue For Loop If True
    :FOR    ${var}    IN    one    two
    \    Continue For Loop If     1 == 1
    \    Fail    Should not be executed
    Should BE Equal    ${var}    two

Continue For Loop If False
    [Documentation]   FAIL Should fail here
    :FOR    ${var}    IN    one    two
    \    Continue For Loop If     1 == 2
    \    Fail    Should fail here

With Continuable Failure After
    [Documentation]    FAIL    Several failures occurred:\n\n1) one\n\n2) three
    :FOR    ${var}    IN    one    two    three
    \       Continue For Loop If    '${var}' == 'two'
    \       Run Keyword And Continue On Failure    Fail    ${var}
    Should Be Equal    ${var}    three

With Continuable Failure Before
    [Documentation]    FAIL    Several failures occurred:\n\n1) one\n\n2) two
    :FOR    ${var}    IN    one    two
    \       Run Keyword And Continue On Failure    Fail    ${var}
    \       Continue For Loop
    \       Fail    This is not executed
    Should Be Equal    ${var}    two

*** Keyword ***
With Loop
    :FOR    ${var}    IN    one    two
    \    Continue For Loop
    \    Fail    Should not be executed
    Should Be Equal    ${var}    two

With Only Continue For Loop
    Continue For Loop
    Fail

With Loop Within Loop
    :FOR    ${var}    IN    one    two
    \    With Loop
    \    Continue For Loop
    \    Fail    Should not be executed
    Should Be Equal    ${var}    two

With Keyword For Loop Calling Keyword With Continue For Loop
    :FOR    ${var}    IN    one    two
    \    With Only Continue For Loop
    \    Fail    Should not be executed
    Should Be Equal    ${var}    two

Continue For Loop In Keyword Teardown
    No Operation
    [Teardown]    With Loop

Invalid Continue For Loop In User Keyword Teardown
    No Operation
    [Teardown]    Continue For Loop
