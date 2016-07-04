*** Settings ***
Library           Exceptions
Suite Teardown    Suite Teardown With Errors

*** Variables ***
${SUITE TEARDOWN FAILED}    SEPARATOR=\n
...    Also parent suite teardown failed:
...    Several failures occurred:
...    ${EMPTY}
...    1) Suite Message 1
...    ${EMPTY}
...    2) Suite Message 2 (with ∏ön ÄßÇïï €§)
...    ${EMPTY}
...    3) No keyword with name 'Missing Keyword' found.

*** Test Cases ***
One Error In Teardown
    [Documentation]    FAIL    Teardown failed:
    ...    Message
    ...    
    ...    ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    One Error

Many Errors In Teardown
    [Documentation]    FAIL    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Message 1
    ...    
    ...    2) Message 2
    ...    
    ...    ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    Many Errors

Errors In Teardown When Setting Variables
    [Documentation]    FAIL    Teardown failed:
    ...    no return value is set
    ...
    ...    ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    Errors when setting variables

Errors In For Loop In Teardown
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
    [Teardown]    Errors In For Loop

Keyword Timeout In Teardown
    [Documentation]    FAIL    Teardown failed:
    ...    Keyword timeout 42 milliseconds exceeded.
    ...
    ...    ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    Timeout

Syntax Error in Teardown
    [Documentation]    FAIL    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Variable '\${non existing variable}' not found.
    ...
    ...    2) No keyword with name 'Keyword Missing' found.
    ...
    ...    ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    Syntax Error

Syntax Error in For Loop in Teardown
    [Documentation]    FAIL    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Variable '${non existing variable}' not found.
    ...
    ...    2) This should be executed
    ...
    ...    3) Variable '${non existing variable}' not found.
    ...
    ...    4) This should be executed
    ...
    ...    ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    Syntax Errors In For Loop

Fatal Error In Teardown
    [Documentation]    FAIL    Teardown failed:
    ...  FatalCatastrophyException
    ...
    ...  ${SUITE TEARDOWN FAILED}
    No Operation
    [Teardown]    Fatal Error


*** Keywords ***
Suite Teardown With Errors
    Fail    Suite Message 1
    Fail    Suite Message 2 (with ∏ön ÄßÇïï €§)
    Missing Keyword
    Log    This As Well Should Be Executed

One Error
    Fail    Message
    Log    This Should Be executed

Many Errors
    Fail    Message 1
    Fail    Message 2
    Log    This Should Also Be Executed

Errors when setting variables
    ${ret} =    Fail    no return value is set
    Should Be Equal    ${ret}    ${None}

Errors In For Loop
    :FOR    ${animal}    IN    cat    dog
    \    Fail    ${animal}
    \    Fail    again

Timeout
    [Timeout]    42 ms
    Sleep    1 s
    Fail    This Should Not Be Executed

Syntax Error
    Log    ${non existing variable}
    Keyword Missing
    Log    This Should Be Executed

Syntax Errors In For Loop
    :FOR    ${i}    IN RANGE    2
    \    Log    ${non existing variable}
    \    Fail    This should be executed
    Log    This should be executed

Fatal Error
    Exit On Failure
    Fail    This Should Not Be Executed
