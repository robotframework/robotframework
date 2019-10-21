*** Settings ***
Force Tags        force1    force2
Library           pass_execution_library.py
Suite Setup       Pass Execution    Hello, world!
Suite Teardown    Pass Execution    Hi, tellus!

*** Test Cases ***
Message is required
    [Documentation]    FAIL    Keyword 'BuiltIn.Pass Execution' expected at least 1 argument, got 0.
    Pass Execution
    Should Not Be Executed

With message
    [Documentation]    PASS    My message
    Pass Execution    ${EMPTY} My message ${SPACE}
    Should Not Be Executed

With HTML message
    [Documentation]    PASS    *HTML*<b>Message</b>
    Pass Execution    *HTML*<b>Message</b>
    Should Not Be Executed

Empty message is not allowed
    [Documentation]    FAIL    Message cannot be empty.
    Pass Execution    ${EMPTY}
    Should Not Be Executed

Only whitesapce message is not allowed
    [Documentation]    FAIL    Message cannot be empty.
    Pass Execution    ${SPACE} ${SPACE}
    Should Not Be Executed

Used in user keyword
    [Documentation]    PASS    Message
    Keyword    Message
    Should Not Be Executed

Used in nested user keyword
    [Documentation]    PASS    Message
    Nested Keyword    Message
    Should Not Be Executed

Used in library keyword raising `PassExecution` exception
    [Documentation]    PASS    Message
    Raise Pass Execution Exception    Message
    Should Not Be Executed

Used in library keyword calling `BuiltIn.pass_execution()` method
    [Documentation]    PASS    Message
    Call Pass Execution Method    Message
    Should Not Be Executed

Used in template keyword
    [Documentation]    PASS    Message
    [Template]    Template keyword
    Message

Used in for loop
    [Documentation]    PASS    Message with 'foo'
    FOR    ${var}    IN    foo    bar
        Pass Execution    Message with '${var}'
        Should Not Be Executed
    END
    Should Not Be Executed

Used in setup
    [Documentation]    PASS    Message
    [Setup]    Run Keywords
    ...    Pass Execution    Message    AND
    ...    Should Not Be Executed
    Should Be Executed
    [Teardown]    Should Be Executed

Used in teardown
    [Documentation]    FAIL    This message is used.
    Fail    This message is NOT used.
    [Teardown]    Run Keywords
    ...    Pass Execution    This message is used.    AND
    ...    Should Not Be Executed

Before failing teardown
    [Documentation]    FAIL
    ...    Teardown failed:
    ...    This message is used.
    Pass Execution    This message is NOT used.
    [Teardown]    Fail    This message is used.

After continuable failure
    [Documentation]    FAIL    Failure
    Run Keyword And Continue On Failure    Fail    Failure
    Pass Execution    This message is not used
    Should Not Be Executed

After continuable failure in user keyword
    [Documentation]    FAIL    My failure
    Keyword With Continuable Failure    My failure
    Should Not Be Executed

After continuable failure in FOR loop
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Failure 1
    ...
    ...    2) Failure 2
    ...
    ...    3) Failure 3
    FOR    ${i}    IN RANGE   1    10
        Run Keyword And Continue On Failure    Fail    Failure ${i}
        Run Keyword If    $i > 2    Run Keywords
        ...    Pass Execution    This message is NOT used    AND
        ...    Should Not Be Executed
    END
    Should Not Be Executed

After continuable failure and before failing teardown
    [Documentation]    FAIL
    ...    The failure
    ...
    ...    Also teardown failed:
    ...    Teardown failure
    Run Keyword And Continue On Failure    Fail    The failure
    Pass Execution    This message is NOT used
    Should Not Be Executed
    [Teardown]    Fail    Teardown failure

After continuable failure in setup
    [Documentation]    FAIL
    ...    Setup failed:
    ...    My failure
    [Setup]    Keyword With Continuable Failure    My failure
    Should Not Be Executed

After continuable failure in teardown
    [Documentation]    FAIL
    ...    Hello
    ...
    ...    Also teardown failed:
    ...    My bad
    Fail    Hello
    [Teardown]    Keyword With Continuable Failure    My bad

After continuable failure in nested user keyword
    [Documentation]    FAIL    Nested keyword fails
    Nested Keyword With Continuable Failure
    Should Not Be Executed

After continuable failure in keyword teardown
    [Documentation]    FAIL
    ...    Keyword fails
    ...
    ...    Also keyword teardown failed:
    ...    Teardown fails
    Keyword With Continuable Failure In Keyword Teardown
    Should Not Be Executed

Pass Execution If when condition is true
    [Documentation]    PASS    Message
    Pass Execution If     1 == 1    Message    tag1    tag2
    Should Not Be Executed

Pass Execution If when condition is false
    Pass Execution If     1 < 0    Message    tag1    tag2
    Should Be Executed

Pass Execution If resolves variables only condition is true
    [Documentation]    FAIL    Variable '${this is not ok}' not found.
    Pass Execution If    False    Message    ${ok not to exist}
    Should Be Executed
    Pass Execution If    True    Message    ${this is not ok}
    Should Not Be Executed

Pass Execution If with multiple variables
    [Documentation]    PASS    My message
    ${msg}=    Set Variable    My message
    @{tags}=    Create List    my    tags
    Pass Execution If    ${True}    ${msg}    @{tags}
    Should Not Be Executed

Remove one tag
    [Documentation]    PASS    Message
    Pass Execution    Message    -force1
    Should Not Be Executed

Remove multiple tags
    [Documentation]    PASS    Message
    Pass Execution    Message    -force1    -force2
    Should Not Be Executed

Remove tags with pattern
    [Documentation]    PASS    Message
    Pass Execution    Message    -force?
    Should Not Be Executed

Set one tag
    [Documentation]    PASS    Message
    Pass Execution    Message    tag
    Should Not Be Executed

Set multiple tags
    [Documentation]    PASS    Message
    Pass Execution    Message    tag1    tag2
    Should Not Be Executed

Set and remove tags
    [Documentation]    PASS    Message
    Pass Execution    Message    -force?    tag1    tag2
    Should Not Be Executed

Set tags are not removed
    [Documentation]    PASS    Message
    Pass Execution    Message    tag1    tag2    -tag?
    Should Not Be Executed

Set tags in teardown
    [Documentation]    PASS    Message
    No Operation
    [Teardown]    Pass Execution    Message    -force?    tag1    tag2

*** Keywords ***
Keyword
    [Arguments]    ${message}
    Pass Execution    ${message}
    Should Not Be Executed

Nested Keyword
    [Arguments]    ${message}
    Keyword    ${message}
    Should Not Be Executed

Template keyword
    [Arguments]    ${message}
    Pass Execution    ${message}
    Should Not Be Executed

Keyword With Continuable Failure
    [Arguments]    ${failure}
    Run Keyword And Continue On Failure    Fail    ${failure}
    Pass Execution    This message DOES NOT override previous failure
    Should Not Be Executed

Nested Keyword With Continuable Failure
    Keyword With Continuable Failure    Nested keyword fails
    Should Not Be Executed

Keyword With Continuable Failure In Keyword Teardown
    Keyword With Continuable Failure    Keyword fails
    Should Not Be Executed
    [Teardown]    Keyword With Continuable Failure    Teardown fails

Should Not Be Executed
    Fail    This keyword should not have been executed

Should Be Executed
    No Operation
