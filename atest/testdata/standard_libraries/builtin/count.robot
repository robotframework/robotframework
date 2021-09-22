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

Should Contain X Times without leading spaces
    [Documentation]    FAIL    '${DICT_5}' contains 'b' 1 time, not 2 times.
    a\ \ a\ \ a    \ a      2    strip_spaces=False
    a\ \ a\ \ a    \ a      3    strip_spaces=Leading
    ${DICT_5}      \n\na    2    strip_spaces=Leading
    ${DICT_5}      \ b      1    strip_spaces=leading
    ${DICT_5}      \nb      2    strip_spaces=LEADING
    ${LIST_4}      \ a      2    strip_spaces=LEADING

Should Contain X Times without trailing spaces
    [Documentation]    FAIL    '${DICT_5}' contains 'd' 1 time, not 2 times.
    a\ \ a\ \ a    a${SPACE}    2    strip_spaces=No
    a\ \ a\ \ a    a${SPACE}    3    strip_spaces=TRailing
    ${DICT_5}      a\t          1    strip_spaces=Trailing
    ${DICT_5}      d\n          1    strip_spaces=TRAILING
    ${DICT_5}      d\t\t        2    strip_spaces=trailing
    ${LIST_4}      b\n\n        2    strip_spaces=trailing

Should Contain X Times without leading and trailing spaces
    [Documentation]    FAIL  '${LIST_4}' contains 'c' 1 time, not 0 times.
    a\ \ a\ \ a    \ a${SPACE}    1    strip_spaces=No
    a\ \ a\ \ a    \ a${SPACE}    3    strip_spaces=Yes
    ${DICT_5}      \n a\t         3    strip_spaces=sure
    ${DICT_5}      \ d\n          2    strip_spaces=TRUE
    ${DICT_5}      \ d\t          2    strip_spaces=true
    ${LIST_4}      \ b\n          2    strip_spaces=${True}
    ${LIST_4}      c              0    strip_spaces=sure thing

Should Contain X Times and do not collapse spaces
    [Documentation]    FAIL  '${LIST_4}' contains '\ \ c' 0 times, not 1 time.
    a\t\ a\n\ a    \ a      2    collapse_spaces=False
    a\n\ a\n\ a    a\n      2    collapse_spaces=${FALSE}
    ${DICT_5}      \ a      1    collapse_spaces=No
    ${LIST_4}      \ \ c    1    collapse_spaces=False

Should Contain X Times and collapse spaces
    [Documentation]    FAIL  '${LIST_4}' contains ' a' 2 times, not 3 times.
    a\ \ a\ \ a    \ a\n    1    collapse_spaces=True
    a\n\ta\t\ a    \ a      2    collapse_spaces=${TRUE}
    ${DICT_5}      \ta      2    collapse_spaces=TRUE
    ${LIST_4}      \ta      3    collapse_spaces=True

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
