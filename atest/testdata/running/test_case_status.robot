*** Settings ***
Library          StandardExceptions.py

*** Test Cases ***
Test Passes
    [Documentation]    PASS
    No Operation

Test Fails
    [Documentation]    FAIL failure
    Fail    failure

Non-Existing Keyword Error
    [Documentation]    FAIL No keyword with name 'Non Existing KW' found.
    Non Existing KW

Test Setup Passes
    [Documentation]    PASS
    [Setup]    No operation
    No Operation

Test Setup Fails
    [Documentation]    FAIL Setup failed:
    ...    failure
    [Setup]    Fail    failure
    Fail    This should not be executed

Test Setup Error
    [Documentation]    FAIL Setup failed:
    ...    No keyword with name 'Non Existing KW' found.
    [Setup]    Non Existing KW
    No Operation

Test Teardown Passes
    [Documentation]    PASS
    No Operation
    [Teardown]    No operation

Test Teardown Fails
    [Documentation]    FAIL Teardown failed:
    ...    failure
    No Operation
    [Teardown]    Fail    failure

Test Teardown Error
    [Documentation]    FAIL Teardown failed:
    ...    No keyword with name 'Non Existing KW' found.
    No Operation
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
    [Setup]    No operation
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

robot.api.Failure
    [Documentation]    FAIL I failed my duties
    Failure

robot.api.Failure with HTML message
    [Documentation]    FAIL *HTML* <b>BANG!</b>
    Failure    <b>BANG!</b>    True

robot.api.Error
    [Documentation]    FAIL I errored my duties
    Error

robot.api.Error with HTML message
    [Documentation]    FAIL *HTML* <b>BANG!</b>
    Error    <b>BANG!</b>    True

*** Keywords ***
Do Nothing
    No operation
