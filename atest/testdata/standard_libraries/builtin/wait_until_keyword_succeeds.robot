*** Settings ***
Library  ExampleLibrary
Library  FailUntilSucceeds.py  3

*** Variables ***
${HELLO}  Used to test that variable name, not value, is shown in arguments


*** Test Cases ***

Fail Because Timeout exceeded
    [Documentation]  FAIL  Timeout 1 second 100 milliseconds exceeded. The last error was: Still 0 times to fail!
    Wait Until Keyword Succeeds  1.1 seconds  555 ms  Fail Until Retried Often Enough

Pass with first Try
    Wait Until Keyword Succeeds  2 minutes  30 seconds  Log  ${HELLO}

Pass With Some Medium Try
    Wait Until Keyword Succeeds  ${42}  200 milliseconds  Fail Until Retried Often Enough

Pass With Last Possible Try
    Wait Until Keyword Succeeds  1.1 seconds  0.3 seconds  Fail Until Retried Often Enough

Pass With Returning Value Correctly
    ${return value} =  Wait Until Keyword Succeeds  4 seconds  0 min 0 sec 1 ms  Fail Until Retried Often Enough  ${HELLO}
    Should Be Equal  ${return value}  ${HELLO}  Returned value should be the one that is given to the keyword.

Invalid Timeout Does Not Cause Uncatchable Failure
    Run Keyword And Expect Error  ValueError: Invalid time string 'Not Time Value'.
    ...  Wait Until Keyword Succeeds  Not Time Value  1 seconds  No Operation

Invalid Retry Interval Does Not Cause Uncatchable Failure
    Run Keyword And Expect Error  ValueError: Invalid time string 'invalid'.
    ...  Wait Until Keyword Succeeds  1 seconds  invalid  No Operation

Wait Until In User Keyword
    Wait Until Inside User Keyword

Failing User Keyword with Wait Until
    [Documentation]  FAIL REGEXP: Timeout 123 milliseconds exceeded. The last error was: Still \\d times to fail!
    Set Times To Fail  10
    Wait Until Keyword Succeeds  ${0.12345}  0.02  User Keyword

Passing User Keyword with Wait Until
    ${return value} =  Wait Until Keyword Succeeds  10 minutes  10 milliseconds  User Keyword
    Should Be Equal  ${return value}  From User Keyword  Returned value should be the one defined in user keyword.

Wait Until With Longer Test Timeout
    [Timeout]  10 seconds
    [Documentation]  FAIL  Timeout 50 milliseconds exceeded. The last error was: My error
    Wait Until Keyword Succeeds  0.05s  0.01s  Fail  My error

Wait Until With Shorter Test Timeout
    [Timeout]  0.1 seconds
    [Documentation]  FAIL  Test timeout 100 milliseconds exceeded.
    Wait Until Keyword Succeeds  1minute  0.1s  Fail  This won't be the final error

Wait Until With Longer Keyword Timeout
    [Documentation]  FAIL  Timeout 100 milliseconds exceeded. The last error was: Error in timeouted UK
    ${timeout} =  Set Variable  1 hour
    Timeouted UK with Wait Until KW

Wait Until With Shorter Keyword Timeout
    [Documentation]  FAIL  Keyword timeout 40 milliseconds exceeded.
    ${timeout} =  Set Variable  40 milliseconds
    Timeouted UK with Wait Until KW

Invalid Number Of Arguments Inside Wait Until Keyword Succeeds
    [Documentation]  FAIL  Keyword 'BuiltIn.No Operation' expected 0 arguments, got 4.
    Wait Until Keyword Succeeds  1 second  0.1s  No Operation  wrong  number  of  arguments

Invalid Keyword Inside Wait Until Keyword Succeeds
    [Documentation]  FAIL  Keyword name must be a string.
    ${list} =  Create List  1  2
    Wait Until Keyword Succeeds  1 second  0.1s  ${list}

Keyword Not Found Inside Wait Until Keyword Succeeds
    [Documentation]  FAIL  No keyword with name 'Non Existing KW' found.
    Wait Until Keyword Succeeds  1 second  0.1s  Non Existing KW


***Keywords***
User Keyword
    ${value} =  Fail Until Retried Often Enough  From User Keyword
    [Return]  ${value}

Wait Until Inside User Keyword
    Wait Until Keyword Succeeds  3.99 seconds  0.1  Fail Until Retried Often Enough

Timeouted UK with Wait Until KW
    [Timeout]  ${timeout}
    Wait Until Keyword Succeeds  100ms  10ms  Fail  Error in timeouted UK
