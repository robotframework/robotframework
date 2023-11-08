*** Settings ***
Default Tags      03    four

*** Test Cases ***
No Own Tags With Default Tags
    No Operation

Own Tags With Default Tags
    [Tags]    FOUR    viisi    00    01    01
    No Operation

Own Tags Empty With Default Tags
    [Tags]
    No Operation
