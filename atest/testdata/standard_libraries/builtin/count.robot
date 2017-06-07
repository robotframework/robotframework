*** Settings ***
Test Template     Should Contain X Times
Variables         variables_to_verify.py

*** Test Cases ***
Get Count
    [Documentation]    Tested also by Should Contain X Times keyword that uses this intenally.
    ...    FAIL STARTS: Converting 'None' to list failed: TypeError:
    [Template]    Verify Get Count
    Hello, world!     o                2
    ${LIST}           b                2
    ${LIST}           cee              1
    ${TUPLE3}         a                1
    ${SPACE * 100}    ${SPACE * 2}     50
    Hello, world!     no match here    0
    ${None}           x

Should Contain X Times with strings
    hello    l        2
    hello    ello     1
    hello    hello    1
    hello    x        0

Should Contain X Times with containers
    ${LIST}    cee      1
    ${LIST}    b        2
    ${LIST}    ${42}    1
    ${LIST}    42       0
    ${DICT}    a        1

Should Contain X Times with Java types
    ${HASHTABLE1}    a    1
    ${ARRAY3}        b    1
    ${VECTOR3}       c    1
    ${VECTOR3}       d    0

Should Contain X Times failing
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 'hello' contains 'l' 2 times, not 3 times.
    ...
    ...    2) 'hello' contains 'lo' 1 time, not 0 times.
    ...
    ...    3) 'hello' contains 'l' 2 times, not 1 time.
    ...
    ...    4) My message
    hello    l      3
    hello    lo     0
    hello    l      1
    hello    xxx    3    My message

Should Contain X Times case-insensitive
    [Documentation]    FAIL    '{'a': 1}' contains 'a' 1 time, not 100 times.
    XxX          X     3      ignore_case=True
    XxX          xx    1      ignore_case=True
    ${DICT}      a     2      ignore_case=yes
    ${DICT}      Ä     2      ignore_case=yes
    ${DICT 1}    a     100    ignore_case=yes, please

Should Contain X Times with invalid item
    [Documentation]    FAIL STARTS: Converting '10' to list failed: TypeError:
    ${10}    a    1

Should Contain X Times with invalid count
    [Documentation]    FAIL STARTS: 'invalid' cannot be converted to an integer: ValueError:
    hello    l    invalid

*** Keywords ***
Verify Get Count
    [Arguments]    ${item1}    ${item2}    ${exp}=0
    ${count} =    Get Count    ${item1}    ${item2}
    ${exp} =    Convert To Integer    ${exp}
    Should Be Equal    ${count}    ${exp}
