*** Test Cases ***
Simple Exit For Loop
    FOR    ${var}    IN    one    two
        Exit For Loop
        Fail    Should not be executed
    END
    Should Be Equal    ${var}    one

Exit For Loop In `Run Keyword`
    FOR    ${var}    IN    one    two    three
        Run Keyword If    '${var}' == 'two'    Exit For Loop
        ${x} =    Set Variable    ${var}-extra
    END
    Should Be Equal    ${x}    one-extra
    Should Be Equal    ${var}    two

Exit For Loop is not supported in user keyword
    [Documentation]    FAIL 'Exit For Loop' can only be used inside a loop.
    FOR    ${var}    IN    one    two
        With Only Exit For Loop
        Fail    Should not be executed
    END
    Should BE Equal    ${var}    one

Exit For Loop In User Keyword With Loop
    FOR    ${var}    IN    one    two
        With Loop
        ${x} =    Set Variable    ${var}-extra
    END
    Should Be Equal    ${x}    two-extra

Exit For Loop In User Keyword With Loop Within Loop
    FOR    ${var}    IN    one    two
        With Loop Within Loop
        ${x} =    Set Variable    ${var}-extra
    END
    Should Be Equal    ${x}    two-extra

Exit For Loop In User Keyword Calling User Keyword With Exit For Loop
    [Documentation]    FAIL 'Exit For Loop' can only be used inside a loop.
    FOR    ${var}    IN    one    two
        With Keyword For Loop Calling Keyword With Exit For Loop
        ${x} =    Set Variable    ${var}-extra
    END
    Should Be Equal    ${x}    two-extra

Exit For Loop Without For Loop Should Fail
   [Documentation]    FAIL 'Exit For Loop' can only be used inside a loop.
   Exit For Loop

Exit For Loop In User Keyword Without For Loop Should Fail
   [Documentation]    FAIL 'Exit For Loop' can only be used inside a loop.
   With Only Exit For Loop

Exit For Loop In Test Teardown
    No Operation
    [Teardown]      With Loop

Exit For Loop In Keyword Teardown
    Exit For Loop In Keyword Teardown

Invalid Exit For Loop In User Keyword Teardown
    [Documentation]    FAIL Keyword teardown failed:
    ...                'Exit For Loop' can only be used inside a loop.
    FOR    ${var}    IN    one   two
        Invalid Exit For Loop In User Keyword Teardown
    END

Exit For Loop If True
    FOR    ${var}    IN    one    two
        Exit For Loop If     1 == 1
        Fail    Should not be executed
    END
    Should BE Equal    ${var}    one

Exit For Loop If False
    [Documentation]   FAIL Should fail here
    FOR    ${var}    IN    one    two
        Exit For Loop If     1 == 2
        Fail    Should fail here
    END

With Continuable Failure After
    [Documentation]    FAIL    Several failures occurred:
    ...
    ...    1) one
    ...
    ...    2) two
    FOR    ${var}    IN    one    two    three    four
        Exit For Loop If    '${var}' == 'three'
        Run Keyword And Continue On Failure    Fail    ${var}
    END
    Should Be Equal    ${var}    three

With Continuable Failure Before
    [Documentation]    FAIL    Several failures occurred:
    ...
    ...    1) one
    ...
    ...    2) two
    ...
    ...    3) three
    FOR    ${var}    IN    one    two    three    four
        Run Keyword And Continue On Failure    Fail    ${var}
        Exit For Loop If    '${var}' == 'three'
    END
    Should Be Equal    ${var}    three

With Continuable Failure In User Keyword
    [Documentation]    FAIL    Several failures occurred:
    ...
    ...    1) å
    ...
    ...    2) ä
    ...
    ...    3) The End
    FOR    ${var}    IN    å    ä    ö
        With Continuable Failure In User Keyword    ${var}
        Exit For Loop If    '${var}' == 'ä'
    END
    Should Be Equal    ${var}    ä
    Fail    The End

*** Keywords ***
With Loop
    FOR    ${var}    IN    one    two
        Exit For Loop
        Fail    Should not be executed
    END
    Should Be Equal    ${var}    one

With Only Exit For Loop
    Exit For Loop
    Fail

With Loop Within Loop
    FOR    ${var}    IN    one    two
        With Loop
        Exit For Loop
        Fail    Should not be executed
    END
    Should Be Equal    ${var}    one

With Keyword For Loop Calling Keyword With Exit For Loop
    FOR    ${var}    IN    one    two
        With Only Exit For Loop
        Fail    Should not be executed
    END
    Should Be Equal    ${var}    one

Exit For Loop In Keyword Teardown
    No Operation
    [Teardown]    With Loop

Invalid Exit For Loop In User Keyword Teardown
    No Operation
    [Teardown]    Exit For Loop

With Continuable Failure In User Keyword
    [Arguments]    ${arg}
    Run Keyword And Continue On Failure    Fail    ${arg}
