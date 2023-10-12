*** Settings ***
Keyword Tags        r1    r2    r3    r4    r5

*** Keywords ***
Remove from keyword using pattern
    [Tags]    r6    -r[2-4]
    No Operation
