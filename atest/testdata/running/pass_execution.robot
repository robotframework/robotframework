*** Settings ***
Force Tags        force1    force2
Library           pass_execution_library.py
Suite Setup       Pass Execution    Hello, world!
Suite Teardown    Pass Execution    Hi, tellus!

*** Test Cases ***

Message is required
    [Documentation]    FAIL Keyword 'BuiltIn.Pass Execution' expected at least 1 argument, got 0.
    Pass Execution
    Fail    should not go here

With message
    [Documentation]    PASS exception message
    Pass Execution    ${EMPTY}exception message ${SPACE}
    Fail    should not go here

With HTML message
    [Documentation]    PASS *HTML*<b>message</b>
    Pass Execution    *HTML*<b>message</b>
    Fail    this should not execute

With empty string as a message
    [Documentation]    FAIL Message cannot be empty.
    Pass Execution    ${EMPTY}
    Fail    this should not execute

With only whitespace as a message
    [Documentation]    FAIL Message cannot be empty.
    Pass Execution    ${SPACE} ${SPACE}
    Fail    this should not execute

Remove one tag
    [Documentation]    PASS message
    Pass Execution    message    -force1
    Fail    should not go here

Remove multiple tags
    [Documentation]    PASS message
    Pass Execution    message    -force1    -force2
    Fail    should not go here

Remove tags with pattern
    [Documentation]    PASS message
    Pass Execution    message    -force?
    Fail    should not go here

Set one tag
    [Documentation]    PASS message
    Pass Execution    message    tag
    Fail    should not go here

Set multiple tags
    [Documentation]    PASS message
    Pass Execution    message    tag1    tag2
    Fail    should not go here

Set and remove tags
    [Documentation]    PASS message
    Pass Execution    message    -force?    tag1    tag2
    Fail    should not go here

Set tags are not removed
    [Documentation]    PASS message
    Pass Execution    message    tag1    tag2    -tag?
    Fail    should not go here

With template
    [Documentation]    PASS message
    [Template]    Template keyword
    message

Inside user keyword
    [Documentation]    PASS message
    A Keyword    message

Inside nested user keyword
    [Documentation]    PASS message
    A Nested Keyword    message

With continuable failure
    [Documentation]    FAIL failure
    Run Keyword And Continue On Failure    Fail    failure
    Pass Execution    message
    Fail    should not go here

With continuable failure in user keyword
    [Documentation]    FAIL this fails
    Keyword with continuable failure    this fails

With continuable failure in FOR loop
    [Documentation]    FAIL failure
    :FOR    ${var}    IN    foo    bar
    \    Run Keyword And Continue On Failure    Fail    failure
    \    Pass Execution    message
    Should Be Equal    ${var}    foo

With continuable failure and test case teardown fails
    [Documentation]    FAIL failure
    ...
    ...                     Also teardown failed:
    ...                     teardown failure
    Run Keyword And Continue On Failure    Fail    failure
    Pass Execution    message
    Fail    this should not run
    [Teardown]    Fail    teardown failure

With test case setup
    [Documentation]    FAIL Setup should succeed
    [Setup]    Pass Execution    message    tag   -force1
    Fail    Setup should succeed

If test case setup fails
    [Documentation]   FAIL Setup failed:
    ...                    setup fail
    [Setup]    Keyword with continuable failure    setup fail
    Fail    this should not be executed

With test case teardown
    [Documentation]    FAIL This message is used.
    Fail    This message is NOT used.
    [Teardown]    Run Keywords
    ...    Pass Execution    This message is used.    AND
    ...    Fail    This keyword is not executed.

If test case teardown fails
    [Documentation]    FAIL Teardown failed:\nThis message is used.
    Pass Execution    This message is NOT used.
    [Teardown]    Fail    This message is used.

Modifying tags in test case teardown should succeed
    [Documentation]    PASS message
    [Teardown]    Pass Execution    message    -force?    tag1    tag2
    No Operation

With for loop
    [Documentation]    PASS message
    :FOR    ${var}    IN    foo    bar    baz
    \    Pass Execution    message    tag
    \    Fail    this should not execute

With library throwing exception
    [Documentation]    PASS message
    Keyword From Library Throws Exception    message
    Fail    this should not execute

With library calling Pass Execution keyword
    [Documentation]    PASS message
    Keyword From Library Calls Builtin    message
    Fail    this should not execute

Should pass execution if condition true
    [Documentation]    PASS message
    Pass Execution If     1 == 1    message    tag1    tag2
    Fail    this should not execute

Should not pass execution if condition false
    [Documentation]   FAIL this should execute
    Pass Execution If     ${False}    message    tag1    tag2
    Fail    this should execute

Should not resolve variables if condition false
    [Documentation]   FAIL this should execute
    Pass Execution If     ${False}    message    ${not_exists}
    Fail    this should execute

Should fail if non-existing variable if condition true
    [Documentation]    FAIL Variable '${not exist}' not found.
    Pass Execution If    ${True}    my message    ${not exist}
    Fail    this should not execute

With multiple variables
    [Documentation]    PASS my message
    ${tag}=    Set Variable    my tag
    ${msg}=    Set Variable    my message
    Pass Execution If    ${True}    ${msg}    ${tag}
    Fail    this should not execute

With continuable failure in test setup
    [Documentation]    FAIL Setup failed:\nmy message
    [Setup]    Keyword with continuable failure    my message
    Fail    should not execute

With continuable failure in test teardown
    [Documentation]    FAIL
    ...    hello
    ...
    ...    Also teardown failed:
    ...    my message
    Fail    hello
    [Teardown]    Keyword with continuable failure    my message

With continuable failure in keyword teardown
    [Documentation]    FAIL
    ...    kw fails
    ...
    ...    Also keyword teardown failed:
    ...    teardown fails
    Keyword with continuable failure in keyword teardown


*** Keywords ***

Template keyword
    [Arguments]    ${message}
    Pass Execution    ${message}
    Fail    should not go here

A Keyword
    [Arguments]    ${message}
    Pass Execution    ${message}
    Fail    should not go here

A Nested Keyword
    [Arguments]    ${message}
    A Keyword   ${message}
    Fail   should not go here either

Keyword with continuable failure
    [Arguments]    ${msg}
    Run Keyword And Continue On Failure    Fail    ${msg}
    Pass Execution    message
    Fail    Should not go here

Keyword with continuable failure in keyword teardown
    Keyword with continuable failure    kw fails
    [Teardown]    Keyword with continuable failure    teardown fails
