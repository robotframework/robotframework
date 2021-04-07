*** Settings ***

*** Variables ***
${HEADER}                 Several failures occurred:

*** Test Cases ***
Continue in test with tag
    [Documentation]    FAIL 1
    [Tags]   robot:continue-on-failure
    Fail   1
    Log    This should be executed

Continue in test with negative tag 
    [Documentation]    FAIL 1
    [Tags]   robot:no-continue-on-failure
    Fail   1
    Fail   2

Continue in user kewyord with tag
    [Documentation]    FAIL 1
    Failure in user keyword using tag

Continue in test with tag and user-kw without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) 1\n\n
    ...    2) 2
    [Tags]   robot:continue-on-failure
    Failure in user keyword without tag
    Log    This should be executed

Continue in test with tag and nested UK with and without tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) 1\n\n
    ...    2) 2
    [Tags]   robot:continue-on-failure
    Failure in user keyword 1
    Log    This should be executed

Continue in for loop with tag
    [Documentation]    FAIL ${HEADER}\n\n
    ...    1) 1\n\n
    ...    2) 2\n\n
    ...    3) 3
    [Tags]   robot:continue-on-failure
    FOR    ${val}    IN    1    2    3
        Fail   ${val}
    END

*** Keywords ***
Failure in user keyword using tag
    [Tags]   robot:continue-on-failure
    Fail   1
    Log    This should be executed

Failure in user keyword without tag
    Fail   1
    Fail   2
    Log    This should be executed

Failure in user keyword 1
    Fail   1
    Failure in user keyword 2 with negative tag
    Log    This should be executed

Failure in user keyword 2 with negative tag
    [Tags]   robot:no-continue-on-failure
    Fail   2
    Log    This should not be executed
    Fail   3
