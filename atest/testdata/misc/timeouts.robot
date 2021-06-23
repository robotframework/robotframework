*** Settings ***
Documentation    Initially created for testing timeouts with testdoc but
...              can be used also for other purposes and extended as needed.
Test Timeout     1min 42s

*** Test Cases ***
Default Test Timeout
    [Documentation]    I have a timeout
    Timeouted

Test Timeout With Variable
    [Timeout]    ${100}
    Timeouted

No Timeout
    [Timeout]    NONE
    No Operation

*** Keywords ***
Timeouted
    [Timeout]    42
    No Operation
