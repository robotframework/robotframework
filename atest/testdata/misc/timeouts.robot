*** Settings ***
Documentation    Initially created for testing timeouts with testdoc but
...              can be used also for other purposes and extended as needed.
Test Timeout     1min 42s

*** Test Cases ***
Default Test Timeout
    [Documentation]    I have a timeout
    Timeouted

Test Timeout With Message
    [Timeout]    1d2h    The message
    Timeouted

Test Timeout With Variable
    [Timeout]    ${100}
    Timeouted

No Timeout
    [Timeout]
    No Operation

*** Keywords ***
Timeouted
    [Timeout]    42    My message
    No Operation
