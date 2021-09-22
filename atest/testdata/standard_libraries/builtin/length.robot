*** Settings ***
Variables         variables_to_verify.py
Variables         length_variables.py

*** Test Cases ***
Get Length
    [Documentation]    FAIL Could not get length of '10'.
    [Template]    Verify Get Length
    ${TUPLE 0}         0
    ${LIST 1}          1
    ${DICT 2}          2
    ${CUSTOM LEN 3}    3
    some string        11
    ${EMPTY}           0
    ${10}              Getting length from an int fails

Length Should Be
    [Documentation]    FAIL Length of '['a', 2]' should be 3 but is 2.
    [Template]    Length Should Be
    ${TUPLE 0}               0
    ${LIST 0}                0
    ${DICT 0}                ${0}
    ${EMPTY}                 ${0.0}
    ${TUPLE 1}               1
    ${LIST 3}                3
    ${DICT 3}                ${3}
    ${CUSTOM LEN 0}          0
    ${CUSTOM LEN 1}          1
    123456789012345678901    ${2.1e1}
    ${LIST 2}                3

Length Should Be with custom message
    [Documentation]    FAIL This fails
    [Template]    Length Should Be
    ${LIST 2}    2    This passes
    ${LIST 2}    3    This fails

Length Should Be with invalid length
    [Documentation]    FAIL STARTS: 'This is not an integer' cannot be converted to an integer: ValueError:
    Length Should Be    ${LIST 2}    This is not an integer

Should Be Empty 1
    [Documentation]    FAIL '['a']' should be empty.
    [Template]    Should Be Empty
    ${TUPLE 0}
    ${LIST 0}
    ${DICT 0}
    ${CUSTOM LEN 0}
    ${EMPTY}
    ${LIST 1}

Should Be Empty 2
    [Documentation]    FAIL '('a', 'b', 'c')' should be empty.
    Should Be Empty    ${TUPLE 3}

Should Be Empty 3
    [Documentation]    FAIL 'åäö' should be empty.
    Should Be Empty    åäö

Should Be Empty with custom message
    [Documentation]    FAIL My non-default error message
    [Template]    Should Be Empty
    ${TUPLE 0}            This succeeds
    Now this will fail    My non-default error message

Should Not Be Empty 1
    [Documentation]    FAIL '{}' should not be empty.
    [Template]    Should Not Be Empty
    ${TUPLE 1}
    \${LIST 2
    ${DICT 3}
    ${CUSTOM LEN 2}
    Non empty string
    ${DICT 0}

Should Not Be Empty 2
    [Documentation]    FAIL '()' should not be empty.
    Should Not Be Empty    ${TUPLE 0}

Should Not Be Empty with custom message
    [Documentation]    FAIL My fine error says () is empty
    [Template]    Should Not Be Empty
    I'm not empty    This would be the error message but there's no failure yet
    ${TUPLE 0}    My fine error says ${TUPLE 0} is empty

Getting length with `length` method
    [Documentation]    FAIL 'length()' should be empty.
    Verify Get Length      ${LENGTH METHOD}    40
    Length Should Be       ${LENGTH METHOD}    40
    Should Not Be Empty    ${LENGTH METHOD}
    Should Be Empty        ${LENGTH METHOD}

Getting length with `size` method
    [Documentation]    FAIL 'size()' should be empty.
    Verify Get Length      ${SIZE METHOD}    41
    Length Should Be       ${SIZE METHOD}    41
    Should Not Be Empty    ${SIZE METHOD}
    Should Be Empty        ${SIZE METHOD}

Getting length with `length` attribute
    [Documentation]    FAIL 'length' should be empty.
    Verify Get Length      ${LENGTH ATTRIBUTE}    42
    Length Should Be       ${LENGTH ATTRIBUTE}    ${42}
    Should Not Be Empty    ${LENGTH ATTRIBUTE}
    Should Be Empty        ${LENGTH ATTRIBUTE}

*** Keywords ***
Verify Get Length
    [Arguments]    ${item}    ${exp}
    ${length} =    Get Length    ${item}
    ${exp} =    Convert To Integer    ${exp}
    Should Be Equal    ${length}    ${exp}
