*** Settings ***
Suite Teardown    Suite Teardown With Failures

*** Variables ***
${SUITE TEARDOWN FAILED}    SEPARATOR=\n
...    Also parent suite teardown failed:
...    Several failures occurred:
...    ${EMPTY}
...    1) Suite Message 1
...    ${EMPTY}
...    2) Suite Message 2 (with ∏ön ÄßÇïï €§)
...    ${EMPTY}
...    3) Variable '\${it is ok not to exist}' not found.

*** Test Cases ***
One Failure
    [Documentation]    FAIL    Teardown failed:
    ...    Message
    ...    
    ...    ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    One Failure

Multiple Failures
    [Documentation]    FAIL    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Message 1
    ...    
    ...    2) Message 2
    ...    
    ...    ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    Multiple Failures

Failure When Setting Variables
    [Documentation]    FAIL    Teardown failed:
    ...    Return values is None
    ...
    ...    ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    Failure when setting variables

Failure In For Loop
    [Documentation]    FAIL    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) cat
    ...    
    ...    2) again
    ...    
    ...    3) dog
    ...    
    ...    4) again
    ...    
    ...    ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    Failures In For Loop

Execution Continues After Test Timeout
    [Documentation]    FAIL    Teardown failed:
    ...    This should be executed
    ...
    ...    ${SUITE TEARDOWN FAILED}
    [Timeout]    0.3 seconds
    No Operation
    [Teardown]    Test Timeout Occurs

Execution Stops After Keyword Timeout
    [Documentation]    FAIL    Teardown failed:
    ...    Keyword timeout 42 milliseconds exceeded.
    ...
    ...    ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    Keyword Timeout Occurs

Execution Continues If Variable Does Not Exist
    [Documentation]    FAIL    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Variable '\${this var does not exist}' not found.
    ...
    ...    2) Variable '\${neither does this one}' not found.
    ...
    ...    ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    Missing Variables

Execution Stops After Syntax Error
    [Documentation]    FAIL    Teardown failed:
    ...    No keyword with name 'Keyword Missing' found.
    ...
    ...    ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    Missing Keywords

Fatal Error 1
    [Documentation]    FAIL    Teardown failed:
    ...  The End
    ...
    ...  ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    Keyword With Fatal Error

Fatal Error 2
    [Documentation]    FAIL    Test execution stopped due to a fatal error.
    ...
    ...  ${SUITE TEARDOWN FAILED}
    Fail    This should not be executed

*** Keywords ***
One Failure
    Fail    Message
    Log    This should be executed

Multiple Failures
    Fail    Message 1
    Fail    Message 2
    Log    This should also be executed

Failure when setting variables
    ${ret} =    Fail    Return values is None
    Should Be Equal    ${ret}    ${None}

Failures In For Loop
    :FOR    ${animal}    IN    cat    dog
    \    Fail    ${animal}
    \    Fail    again

Test Timeout Occurs
    Sleep    1 s
    Fail    This should be executed

Keyword Timeout Occurs
    [Timeout]    42 ms
    Sleep    1 s
    Fail    This should not be executed

Missing Variables
    Log    ${this var does not exist}
    Log    This should be executed
    :FOR    ${i}    IN RANGE    1
    \    Fail    ${neither does this one}

Missing Keywords
    Keyword Missing
    Log    This should be executed
    Another Missing Keyword

Keyword With Fatal Error
    Fatal Error    The End
    Fail    This Should Not Be Executed

Suite Teardown With Failures
    Fail    Suite Message 1
    Fail    Suite Message 2 (with ∏ön ÄßÇïï €§)
    Log    ${it is ok not to exist}
    Log    This should be executed
