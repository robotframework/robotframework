*** Variables ***
@{ESCAPING}    c:\\temp    \${not var}    \x00\\x00    ELSE    \n\\n    ${/}

*** Test Cases ***
Return one value
    ${ret} =    Return one value    42
    Should Be Equal    ${ret}    ${42}

Return multiple values
    @{ret} =    Return multiple values
    ${ret} =    Catenate    SEPARATOR=-    @{ret}
    Should Be Equal    ${ret}    1-2-3-4

Return nothing
    ${ret} =    Return nothing
    Should Be Equal    ${ret}    ${NONE}

Nested usage
    ${ret} =    Nested usage
    Should Be Equal    ${ret}    Nested return value

Keyword fails
    [Documentation]    FAIL    Expected error
    Keyword fails

Inside Run Keyword variants
    [Documentation]    FAIL
    ...    Continuable
    ...
    ...    Also teardown failed:
    ...    Continuable
    ${ret} =    Inside Run Keyword If
    Should Be Equal    ${ret}    Run Kw If
    ${ret} =    Inside Run Keywords
    Should Be Equal    ${ret}    Run Kws
    [Teardown]    Inside Run Keywords

Using Run Keyword variants
    ${ret} =    Using Run Keyword If
    Should Be Equal    ${ret}    Nested return value
    ${ret} =    Using Run Keywords
    Should Be Equal    ${ret}    This is returned
    [Teardown]    Using Run Keywords

Outside user keyword
    [Documentation]    FAIL Invalid 'RETURN' usage.
    Run Keyword And Return    Log    This does not work
    Fail    This is not executed

With list variable containing escaped items
    [Documentation]    FAIL No keyword with name 'c:\\temp' found.
    ${ret} =    Run Keyword And Return With Variables    Create List    @{ESCAPING}
    Should Be Equal    ${ret}    ${ESCAPING}
    Run Keyword And Return With Variables    @{ESCAPING}

Return strings that needs to be escaped
    ${ret} =    Run Keyword And Return Given Args    \${not var}
    Should Be Equal    ${ret}    \${not var}
    ${ret} =    Run Keyword And Return Given Args    c:\\temp\\new
    Should Be Equal    ${ret}    c:\\temp\\new
    ${ret} =    Run Keyword And Return Given Args    @{ESCAPING}
    Should Be Equal    ${ret}    ${ESCAPING}

Run Keyword And Return If
    ${ret} =    Run Keyword And Return If Arg Is Positive
    Should Be Equal    ${ret}    No positive arguments
    ${ret} =    Run Keyword And Return If Arg Is Positive    -1  -2  -3
    Should Be Equal    ${ret}    No positive arguments
    ${ret} =    Run Keyword And Return If Arg Is Positive    -1  0  1  2
    Should Be Equal    ${ret}    1 > 0

Run Keyword And Return If can have non-existing keywords and variables if condition is not true
    [Documentation]    FAIL No keyword with name 'Non-Existing Keyword When Condition Is True' found.
    Run Keyword And Return If With Non-Existing Keyword And Variables

Run Keyword And Return If with list variable containing escaped items
    [Documentation]    FAIL STARTS: Evaluating expression 'c:\\\\temp' failed:
    ${ret} =    Run Keyword And Return If With Variables    True   Create List    @{ESCAPING}
    Should Be Equal    ${ret}    ${ESCAPING}
    Run Keyword And Return If With Variables    @{ESCAPING}

Run Keyword And Return If return strings that needs to be escaped
    ${ret} =    Run Keyword And Return Given Args If    True    \${not var}
    Should Be Equal    ${ret}    \${not var}
    ${ret} =    Run Keyword And Return Given Args If   True    c:\\temp\\new
    Should Be Equal    ${ret}    c:\\temp\\new
    ${ret} =    Run Keyword And Return Given Args If    1 > 0    @{ESCAPING}
    Should Be Equal    ${ret}    ${ESCAPING}
    ${ret} =    Run Keyword And Return Given Args If    False    @{ESCAPING}
    Should Be Equal    ${ret}    ${NONE}

Run Keyword And Return In Teardown
    No Operation
    [Teardown]    Run Keyword And Return In Teardown

Run Keyword And Return In Teardown When Keyword Fails
    [Documentation]    FAIL    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Expected error
    ...
    ...    2) No keyword with name 'Non-Existing Keyword When Condition Is True' found.
    ...
    ...    3) Another expected error
    ...
    ...    Also keyword teardown failed:
    ...    Expected error
    No Operation
    [Teardown]    Run Keyword And Return In Teardown When Keyword Fails

*** Keywords ***
Return one value
    [Arguments]    ${arg}
    Run Keyword And Return    Convert To Integer    ${arg}
    Fail    Not executed
    [Return]    Not returned

Return multiple values
    Run Keyword And Return    Create List    1    2    3    4
    Fail    Not executed
    [Return]    Not returned

Return nothing
    Run Keyword And Return    Log    No return value
    Fail    Not executed
    [Return]    Not returned

Nested usage
    Run Keyword And Return    Nested
    Fail    Not executed
    [Return]    Not returned

Nested
    Run Keyword And Return     Set Variable    Nested return value
    Fail    Not executed
    [Return]    Not returned

Keyword fails
    Run Keyword And Return    Fail    Expected error
    Fail    Not executed
    [Return]    Not returned

Inside Run Keyword If
    Run Keyword If    0    Run Keyword And Return    Fail
    Run Keyword If    1    Run Keyword And Return    Set Variable    Run Kw If
    Fail    Not executed
    [Return]    Not returned

Inside Run Keywords
    Run Keywords
    ...    Log    First keyword    AND
    ...    Run Keyword And Continue On Failure    Fail    Continuable    AND
    ...    Run Keyword And Return    Set Variable    Run Kws    AND
    ...    Fail    Not executed 1
    Fail    Not executed 2
    [Return]    Not returned

Using Run Keyword If
    Run Keyword And Return    Run Keyword If    0    Fail    ELSE    Nested
    Fail    Not executed
    [Return]    Not returned

Using Run Keywords
    Run Keyword And Return    Run Keywords
    ...    Set Variable    This is not returned    AND
    ...    Log    Second keyword    AND
    ...    Run Keyword And Return    Set Variable    This is returned    AND
    ...    Fail    Not executed
    Fail    Not executed
    [Return]    Not returned

Run Keyword And Return With Variables
    [Arguments]    @{args}
    Run Keyword And Return    @{args}

Run Keyword And Return Given Args
    [Arguments]    @{return}
    Run Keyword And Return    Set Variable    @{return}

Run Keyword And Return Given Args If
    [Arguments]    ${condition}    @{return}
    Run Keyword And Return If    ${condition}    Set Variable    @{return}

Run Keyword And Return If Arg Is Positive
    [Arguments]    @{args}
    FOR    ${arg}    IN    @{args}
        Run Keyword And Return If    ${arg} > 0    Set Variable    ${arg} > 0
    END
    Run Keyword And Return If    True    Set Variable    No positive arguments
    Fail    Not executed
    [Return]    Not returned

Run Keyword And Return If With Non-Existing Keyword And Variables
    Run Keyword And Return If    False    Non-Existing Keyword
    Run Keyword And Return If    False    Set Variable    ${non-existing variable}
    Run Keyword And Return If    True    Non-Existing Keyword When Condition Is True
    Fail    Not executed
    [Return]    Not returned

Run Keyword And Return If With Variables
    [Arguments]    @{args}
    Run Keyword And Return If    @{args}

Run Keyword And Return In Teardown
    ${ret} =    Return One Value    42
    Should Be Equal    ${ret}    ${42}
    ${ret} =    Run Keyword And Return Given Args If    True    return value
    Should Be Equal    ${ret}    return value
    Run Keyword And Return    No Operation
    Fail    Not executed
    [Return]    Not returned
    [Teardown]    Return One Value    42

Run Keyword And Return In Teardown When Keyword Fails
    Keyword Fails
    Run Keyword And Return If With Non-Existing Keyword And Variables
    Run Keyword And Return    Fail    Another expected error
    Fail    Not executed
    [Return]    Not returned
    [Teardown]    Keyword Fails
