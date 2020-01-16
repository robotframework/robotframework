*** Settings ***
Test Timeout      500 milliseconds    Not supported anymore

*** Test Cases ***
Default Test Timeout Message
    No operation

Test Timeout Message
    [Timeout]    100 milliseconds    My test timeout message
    No operation

Test Timeout Message In Multiple Columns
    [Timeout]    1 millisecond    My    test     timeout     message
    ...    in
    ...    multiple columns
    No operation

Keyword Timeout Message
    Keyword Timeout Message

Keyword Timeout Message In Multiple Columns
    Keyword Timeout Message In Multiple Columns

*** Keywords ***
Keyword Timeout Message
    [Timeout]    1 second    My keyword timeout message
    No operation

Keyword Timeout Message In Multiple Columns
    [Timeout]    111 milliseconds    My    keyword     timeout    message
    ...    in
    ...    multiple columns
    No operation
