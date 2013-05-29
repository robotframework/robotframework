*** Setting ***
Force Tags        01    ${EMPTY}    02    @{EMPTY}
Default Tags      @{DEFAULTS}

*** Variables ***
@{DEFAULTS}       03    ${EMPTY}    four


*** Test Case ***
No Own Tags
    No Operation

Own Tags
    [Tags]    FOUR    viisi    @{EMPTY}    00    ${EMPTY}    01    01
    No Operation

Own Tags Empty
    [Tags]
    No Operation
