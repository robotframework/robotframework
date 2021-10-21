*** Test Cases ***
Inline if passing
    IF    True    Log    reached this

Inline if failing
    [Documentation]    FAIL failing inside if
    IF    '1' == '1'   Fail    failing inside if

Inline if not executed
    IF    False    Fail    should not go here

Inline if not executed failing
    [Documentation]    FAIL after not passing
    IF    'a' == 'b'   Pass Execution    should not go here
    Fail    after not passing

Inline if else - if executed
    IF    1 > 0    Log    does go through here    ELSE    Fail    should not go here

Inline if else - else executed
    IF    0 > 1    Fail    should not go here    ELSE    Log    does go through here

Inline if else - if executed - failing
    [Documentation]    FAIL expected
    IF    1 > 0    Fail    expected    ELSE    Log    unexpected

Inline if else - else executed - failing
    [Documentation]    FAIL expected
    IF    0 > 1    Log    unexpected    ELSE    Fail    expected

Assignment inside inline if
    IF    True    ${num}=   Convert to number    12
    Variable Should Exist    $num

Inline if inside for loop
    [Documentation]    FAIL The end
    FOR    ${i}    IN    1    2    3
        IF    ${i} == 3    Fail    The end    ELSE    Log    ${i}
    END

Inline if inside nested loop
    [Documentation]    FAIL The end
    IF    ${False}
       Fail    Should not go here
    ELSE
        FOR    ${i}    IN    1    2    3
            IF    ${i} == 3    Fail    The end    ELSE    Log    ${i}
        END
    END

Inline if passing in keyword
    Passing if keyword

Inline if passing in else keyword
    Passing else keyword

Inline if failing in keyword
    [Documentation]    FAIL expected
    Failing if keyword

Inline if failing in else keyword
    [Documentation]    FAIL expected
    Failing else keyword

Invalid END after inline header
    [Documentation]    FAIL 'End' is a reserved keyword. It must be an upper case 'END' and follow an opening 'FOR' or 'IF' when used as a marker.
    IF    True    Log    reached this
        Log   this is a normal keyword call
    END


*** Keywords ***
Passing if keyword
    IF    ${1}    Log    expected    ELSE IF    12 < 14    Fail    should not go here    ELSE    Fail    not here

Passing else keyword
    IF    ${False}    Fail    not here    ELSE    Log    expected

Failing if keyword
    IF    ${1}    Fail    expected    ELSE IF    12 < 14    Log    should not go here    ELSE    Log    not here

Failing else keyword
    IF    ${False}    Log    should not here    ELSE    Fail    expected
