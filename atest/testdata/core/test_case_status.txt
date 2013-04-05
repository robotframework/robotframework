*** Test Case ***
Test Pass
    [Documentation]    PASS
    NOOP

Test Fail
    [Documentation]    FAIL failure
    Fail    failure

Test Error
    [Documentation]    FAIL error
    Error    error

Test Error Non Existing KW
    [Documentation]    FAIL No keyword with name 'Non Existing KW' found.
    Non Existing KW

Tests Setup Pass
    [Documentation]    PASS
    [Setup]    Noop
    NOOP

Tests Setup Fail
    [Documentation]    FAIL Setup failed:
    ...    failure
    [Setup]    Fail    failure
    Fail    This should not be executed

Tests Setup Error
    [Documentation]    FAIL Setup failed:
    ...    error
    [Setup]    Error    error
    Fail    This should not be executed

Tests Setup Error Non Existing KW
    [Documentation]    FAIL Setup failed:
    ...    No keyword with name 'Non Existing KW' found.
    [Setup]    Non Existing KW
    NOOP

Tests Teardown Pass
    [Documentation]    PASS
    NOOP
    [Teardown]    Noop

Tests Teardown Fail
    [Documentation]    FAIL Teardown failed:
    ...    failure
    NOOP
    [Teardown]    Fail    failure

Tests Teardown Error
    [Documentation]    FAIL Teardown failed:
    ...    error
    NOOP
    [Teardown]    Error    error

Tests Teardown Error Non Existing KW
    [Documentation]    FAIL Teardown failed:
    ...    No keyword with name 'Non Existing KW' found.
    NOOP
    [Teardown]    Non Existing KW

Test And Teardown Fails
    [Documentation]    FAIL failure
    ...
    ...    Also teardown failed:
    ...    Teardown failed
    Fail    failure
    [Teardown]    Fail    Teardown failed

Test Setup And Teardown Pass
    [Documentation]    PASS
    [Setup]    Noop
    Log    Hello, world
    [Teardown]    Do Nothing

Test Teardown is Run When Setup Fails
    [Documentation]    FAIL Setup failed:
    ...    No keyword with name 'Non Existing Keyword' found.
    [Setup]    Non Existing Keyword    whatever
    Fail    This should not be run
    [Teardown]    Log    Hello from teardown!

Test Setup And Teardown Fails
    [Documentation]    FAIL Setup failed:
    ...    Setup failure
    ...
    ...    Also teardown failed:
    ...    Teardown failure
    [Setup]    Fail    Setup failure
    Fail    This should not be run
    [Teardown]    Fail    Teardown failure

*** Keyword ***
Do Nothing
    Noop
