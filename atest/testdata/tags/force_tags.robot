*** Settings ***
Force Tags        01    02

*** Test Cases ***
No Own Tags With Force Tags
    No Operation

Own Tags With Force Tags
    [Tags]    FOUR    viisi    00    01    01
    No Operation

Own Tags Empty With Force Tags
    [Tags]
    No Operation
