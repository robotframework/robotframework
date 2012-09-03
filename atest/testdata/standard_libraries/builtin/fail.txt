*** Settings ***
Force Tags    force1    force2


*** Test Cases ***
Fail
    [Documentation]    FAIL AssertionError
    Fail

Fail With Message
    [Documentation]    FAIL Failure message
    Fail    Failure message

Set one tag
    [Documentation]    FAIL Message
    Fail    Message    tag

Set multiple tags
    [Documentation]    FAIL Message
    Fail    Message    tag1    tag2

Remove one tag
    [Documentation]    FAIL Message
    Fail    Message    -force1

Remove multiple tags
    [Documentation]    FAIL Message
    Fail    Message    -force1    -force2

Remove multiple tags with pattern
    [Documentation]    FAIL Message
    Fail    Message    -force?

Set and remove tags
    [Documentation]    FAIL Message
    Fail    Message    tag1    -force1    tag2    -nonEx

Set tags should not be removed
     [Documentation]    FAIL Message
     Fail    Message    foo     -f*    fii
