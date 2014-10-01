*** Variables ***
${COUNTER}         ${0}
${PASS MESSAGE}    -PASSED -ALL
${FAIL MESSAGE}    -ALL +PASSED
${REMOVED FOR MESSAGE}     -FOR -ALL
${KEPT FOR MESSAGE}        +FOR -ALL
${REMOVED WUKS MESSAGE}    -WUKS -ALL
${KEPT WUKS MESSAGE}       +WUKS -ALL
${REMOVED BY NAME MESSAGE}    -BYNAME -ALL
${KEPT BY NAME MESSAGE}    +BYNAME -ALL
${REMOVED BY PATTERN MESSAGE}    -BYPATTERN -ALL
${KEPT BY PATTERN MESSAGE}    +BYPATTERN -ALL

*** Test Case ***

Passing
    Log    ${PASS MESSAGE}

Failing
    [Documentation]    FAIL Message
    Log     ${FAIL MESSAGE}
    Fail    Message

For when test fails
    [Documentation]    FAIL Cannot pass
    My FOR
    Fail    Cannot pass

For when test passes
    My FOR

WUKS when test fails
    [Documentation]    FAIL Cannot pass
    Wait Until Keyword Succeeds    2s    0.01s    My WUKS
    Fail    Cannot pass

WUKS when test passes
     Wait Until Keyword Succeeds    2s    0.01s    My WUKS

NAME when test passes
    Remove By Name
    Do not remove by name

NAME when test fails
    [Documentation]    FAIL this fails
    Remove By Name
    Do not remove by name
    Fail    this fails

NAME with * pattern when test passes
    This should be removed
    This should be removed also
    This should not be removed

NAME with * pattern when test fails
    [Documentation]    FAIL this fails
    This should be removed
    This should be removed also
    This should not be removed
    Fail    this fails

NAME with ? pattern when test passes
    RemoveYES
    RemoveNO

NAME with ? pattern when test fails
    [Documentation]    FAIL this fails
    RemoveYES
    RemoveNO
    Fail    this fails

*** Keywords ***

My FOR
    :FOR    ${item}    IN    one    two    three    LAST
    \    Run Keyword If    "${item}" == "LAST"
    \    ...    Log    ${KEPT FOR MESSAGE} ${item}
    \    ...    ELSE
    \    ...    Log    ${REMOVED FOR MESSAGE} ${item}

My WUKS
    Set Test Variable    $COUNTER    ${COUNTER + 1}
    Run Keyword If    ${COUNTER} < 10    Fail    ${REMOVED WUKS MESSAGE}
    Run Keyword If    ${COUNTER} == 10    Fail    ${KEPT WUKS MESSAGE}

Remove By Name
    Log    ${REMOVED BY NAME MESSAGE}

Do not remove by name
    Remove By Name
    Log    ${KEPT BY NAME MESSAGE}

This should be removed
    Log    ${REMOVED BY PATTERN MESSAGE}

This should be removed also
    Log    ${REMOVED BY PATTERN MESSAGE}

This should not be removed
    This should be removed
    Log    ${KEPT BY PATTERN MESSAGE}

RemoveYES
    Log    ${REMOVED BY PATTERN MESSAGE}

RemoveNO
    RemoveYES
    Log    ${KEPT BY PATTERN MESSAGE}
