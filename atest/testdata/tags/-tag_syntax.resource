*** Settings ***
Keyword Tags        r1    r2    r3    r4    r5

*** Keywords ***
Remove from keyword using pattern
    [Tags]    r6    -r[2-4]
    No Operation

Remove from keyword using operator
    [Tags]    -NOT r1 OR nonex
    No Operation

Deprecated operator usage in keyword
    [Tags]    -NOTR1ORnonex
    No Operation
