*** Settings ***
Library           ExampleLibrary
Library           FailUntilSucceeds.py    3

*** Variables ***
${HELLO}          Used to test that variable name, not value, is shown in arguments

*** Test Cases ***
Fail Because Timeout exceeded
    [Documentation]    FAIL GLOB:
    ...    Keyword 'Fail Until Retried Often Enough' failed after retrying for 100 milliseconds. \
    ...    The last error was: Still ? times to fail!
    Wait Until Keyword Succeeds    0.1 seconds    55ms    Fail Until Retried Often Enough

Pass with first Try
    Wait Until Keyword Succeeds    2 minutes    30 seconds    Log    ${HELLO}

Pass With Some Medium Try
    Wait Until Keyword Succeeds    ${42}    2 milliseconds    Fail Until Retried Often Enough

Pass With Last Possible Try
    Wait Until Keyword Succeeds    1.1 seconds    0.3 seconds    Fail Until Retried Often Enough

Pass With Returning Value Correctly
    ${return value} =    Wait Until Keyword Succeeds    4 seconds    0 min 0 sec 1 ms
    ...    Fail Until Retried Often Enough    ${HELLO}
    Should Be Equal    ${return value}    ${HELLO}

Invalid Timeout Does Not Cause Uncatchable Failure
    Run Keyword And Expect Error
    ...    ValueError: Invalid time string 'Not Time Value'.
    ...    Wait Until Keyword Succeeds    Not Time Value    1 seconds    No Operation

Invalid Retry Interval Does Not Cause Uncatchable Failure
    Run Keyword And Expect Error
    ...    ValueError: Invalid time string 'invalid'.
    ...    Wait Until Keyword Succeeds    1 seconds    invalid    No Operation

Wait Until In User Keyword
    Wait Until Inside User Keyword

Failing User Keyword with Wait Until
    [Documentation]    FAIL GLOB:
    ...    Keyword 'User Keyword' failed after retrying for 123 milliseconds. \
    ...    The last error was: Still ? times to fail!
    Set Times To Fail    10
    Wait Until Keyword Succeeds    ${0.12345}    0.02    User Keyword

Passing User Keyword with Wait Until
    ${return value} =    Wait Until Keyword Succeeds    10 minutes    10 milliseconds    User Keyword
    Should Be Equal    ${return value}    From User Keyword

Wait Until With Longer Test Timeout
    [Documentation]    FAIL
    ...    Keyword 'Fail' failed after retrying for 50 milliseconds. \
    ...    The last error was: My error
    [Timeout]    10 seconds
    Wait Until Keyword Succeeds    0.05s    0.01s    Fail    My error

Wait Until With Shorter Test Timeout
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1 seconds
    Wait Until Keyword Succeeds    1minute    0.1s    Fail    This won't be the final error

Wait Until With Longer Keyword Timeout
    [Documentation]    FAIL
    ...    Keyword 'Fail' failed after retrying for 100 milliseconds. \
    ...    The last error was: Error in timeouted UK
    Timeouted UK with Wait Until KW    1 hour

Wait Until With Shorter Keyword Timeout
    [Documentation]    FAIL Keyword timeout 40 milliseconds exceeded.
    Timeouted UK with Wait Until KW     40 milliseconds

Retry as count
    Wait Until Keyword Succeeds    4 times    0 s    Fail Until Retried Often Enough
    Wait Until Keyword Succeeds    99999TIMES    42ms    No Operation
    Wait Until Keyword Succeeds    10 x    -1    Fail Until Retried Often Enough
    Wait Until Keyword Succeeds    ${1}X    1 minute 2 seconds    No Operation

Retry as count failing 1
    [Documentation]    FAIL
    ...    Keyword 'Fail Until Retried Often Enough' failed after retrying 3 times. \
    ...    The last error was: Still 0 times to fail!
    Wait Until Keyword Succeeds    3 times    2 ms    Fail Until Retried Often Enough

Retry as count failing 2
    [Documentation]    FAIL
    ...    Keyword 'Fail Until Retried Often Enough' failed after retrying 1 time. \
    ...    The last error was: Still 2 times to fail!
    Wait Until Keyword Succeeds    1X    1 day    Fail Until Retried Often Enough

Retry count must be integer 1
    [Documentation]    FAIL STARTS: 'xx' cannot be converted to an integer: ValueError:
    Wait Until Keyword Succeeds    XXX    0    No Operation

Retry count must be integer 2
    [Documentation]    FAIL STARTS: '3.14' cannot be converted to an integer: ValueError:
    Wait Until Keyword Succeeds    3.14 times    1s    No Operation

Retry count must be positive 1
    [Documentation]    FAIL ValueError: Retry count 0 is not positive.
    Wait Until Keyword Succeeds    0 Times    1s    No Operation

Retry count must be positive 2
    [Documentation]    FAIL ValueError: Retry count -8 is not positive.
    Wait Until Keyword Succeeds    -8x    1s    No Operation

No retry after syntax error
    [Documentation]    FAIL FOR loop cannot be empty.
    Wait Until Keyword Succeeds    10 second    1s    Syntax Error

No retry if keyword name is not string
    [Documentation]    FAIL Keyword name must be a string.
    ${list} =    Create List    1    2
    Wait Until Keyword Succeeds    1 second    0.1s    ${list}

Retry if keyword is not found
    [Documentation]    FAIL
    ...    Keyword 'Non Existing KW' failed after retrying for 300 milliseconds. \
    ...    The last error was: No keyword with name 'Non Existing KW' found.
    Wait Until Keyword Succeeds    0.3s    0.1s    Non Existing KW

Retry if wrong number of arguments
    [Documentation]    FAIL
    ...    Keyword 'No Operation' failed after retrying for 50 milliseconds. \
    ...    The last error was: Keyword 'BuiltIn.No Operation' expected 0 arguments, got 3.
    Wait Until Keyword Succeeds    0.05 second    0.01s    No Operation    No    args    accepted

Retry if variable is not found
    [Documentation]    FAIL
    ...    Keyword 'Access Nonexisting Variable' failed after retrying 3 times. \
    ...    The last error was: Variable '\${nonexisting}' not found.
    Wait Until Keyword Succeeds    3 times    0s    Access Nonexisting Variable

Pass With Initially Nonexisting Variable Inside Wait Until Keyword Succeeds
    Wait Until Keyword Succeeds    3 times    0s    Access Initially Nonexisting Variable

Strict retry interval
    Wait Until Keyword Succeeds    4 times    strict: 100ms    Fail Until Retried Often Enough

Fail with strict retry interval
    [Documentation]    FAIL
    ...    Keyword 'Fail Until Retried Often Enough' failed after retrying 3 times. \
    ...    The last error was: Still 0 times to fail!
    Wait Until Keyword Succeeds    3 times    STRICT : 0.1s    Fail Until Retried Often Enough

Strict retry interval violation
    Wait Until Keyword Succeeds    5 sec    strict:0.1    Fail Until Retried Often Enough    sleep=0.101

Strict and invalid retry interval
    [Documentation]    FAIL    ValueError: Invalid time string 'invalid:value'.
    Wait Until Keyword Succeeds    3 times    strict: invalid:value    Not executed

Keyword name as variable
    [Documentation]    FAIL
    ...    Keyword 'Fail' failed after retrying 2 times. \
    ...    The last error was: Hello!
    VAR    ${passing}    Log
    VAR    ${failing}    Fail
    Wait Until Keyword Succeeds    2 hours    0    ${passing}    Hello!
    Wait Until Keyword Succeeds    2 times    0    ${failing}    Hello!

*** Keywords ***
User Keyword
    ${value} =    Fail Until Retried Often Enough    From User Keyword
    RETURN    ${value}

Wait Until Inside User Keyword
    Wait Until Keyword Succeeds    3.99 seconds    0.1    Fail Until Retried Often Enough

Timeouted UK with Wait Until KW
    [Arguments]    ${timeout}
    [Timeout]    ${timeout}
    Wait Until Keyword Succeeds    100ms    10ms    Fail    Error in timeouted UK

Access Nonexisting Variable
    Log    ${nonexisting}
    Fail    Should NEVER be executed

Access Initially Nonexisting Variable
    Log    ${created after accessing first time}
    [Teardown]    Set Test Variable    ${created after accessing first time}    created in keyword teardown

Syntax Error
    FOR    ${x}    IN    cannot    have    empty    body
    END
