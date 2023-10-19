*** Variables ***
&{dict}

*** Test Cases ***
IF passing
    IF    True    Log    reached this

IF failing
    [Documentation]    FAIL Inside IF
    IF    '1' == '1'   Fail    Inside IF

IF erroring
    [Documentation]    FAIL No keyword with name 'Oooops, I don't exist!' found.
    IF    '1' == '1'   Oooops, I don't exist!

Not executed
    [Documentation]    FAIL After IF
    IF    False    Not    run
    Fail    After IF

Not executed after failure
    [Documentation]    FAIL Before IF
    Fail    Before IF
    IF    True    Not    run    ELSE IF    True    Not run    ELSE    Not run

Not executed after failure with assignment
    [Documentation]    FAIL Before IF
    Fail    Before IF
    ${x} =          IF    True    Not run    ELSE    Not run
    ${x}    @{y}    IF    True    Not run    ELSE    Not run

ELSE IF not executed
    [Documentation]    FAIL Expected failure
    IF    False    Not run    ELSE IF    False    Not    run    ELSE    Executed
    IF    1 > 0    Failure    ELSE IF    True    Not run        ELSE IF    True    Not run

ELSE IF executed
    [Documentation]    FAIL Expected failure
    IF    False    Not run    ELSE IF    True    Executed    ELSE    Not run
    IF                False    Not run
    ...    ELSE IF    False    Not run
    ...    ELSE IF    True     Failure
    ...    ELSE IF    False    Not run
    ...    ELSE                Not run

ELSE not executed
    [Documentation]    FAIL expected
    IF    1 > 0    Executed            ELSE    Not    run
    IF    1 > 0    Fail    expected    ELSE    Not run

ELSE executed
    [Documentation]    FAIL expected
    IF    0 > 1    Not run       ELSE    Log    does go through here
    IF    0 > 1    Not    run    ELSE    Fail    expected

Assign
    ${x} =    IF    1    Convert to integer    1    ELSE IF    2    Convert to integer    2    ELSE    Convert to integer    3
    ${y} =    IF    0    Convert to integer    1    ELSE IF    2    Convert to integer    2    ELSE    Convert to integer    3
    ${z} =    IF    0    Convert to integer    1    ELSE IF    0    Convert to integer    2    ELSE    Convert to integer    3
    Should Be Equal    ${x}    ${1}
    Should Be Equal    ${y}    ${2}
    Should Be Equal    ${z}    ${3}

Assign with item
    ${dict}[x] =    IF    1    Convert to integer    1    ELSE IF    2    Convert to integer    2    ELSE    Convert to integer    3
    ${dict}[y] =    IF    0    Convert to integer    1    ELSE IF    2    Convert to integer    2    ELSE    Convert to integer    3
    ${dict}[z] =    IF    0    Convert to integer    1    ELSE IF    0    Convert to integer    2    ELSE    Convert to integer    3
    Should Be Equal    ${dict}[x]    ${1}
    Should Be Equal    ${dict}[y]    ${2}
    Should Be Equal    ${dict}[z]    ${3}

Multi assign
    [Documentation]    FAIL Cannot set variables: Expected 3 return values, got 2.
    ${x}    ${y}    ${z} =    IF    True    Create list    a    b    c    ELSE    Not run
    Should Be Equal    ${x}    a
    Should Be Equal    ${y}    b
    Should Be Equal    ${z}    c
    ${x}    ${y}    ${z} =    IF    True    Create list    too    few    ELSE    Not run

List assign
    @{x} =    IF    True    Create list    a    b    c    ELSE    Not run
    Should Be True    ${x} == ['a', 'b', 'c']
    ${x}    @{y}    ${z} =    IF    False    Not run    ELSE    Create list    a    b    c
    Should Be Equal    ${x}    a
    Should Be True     ${y} == ['b']
    Should Be Equal    ${z}    c

Dict assign
    &{x} =    IF    False    Not run    ELSE    Create dictionary    a=1    b=2
    Should Be True    ${x} == {'a': '1', 'b': '2'}

Assign based on another variable
    VAR    ${x}    y
    ${${x}} =    IF    True    Set Variable    Y    ELSE    Not run
    Should Be Equal    ${y}    Y

Assign without ELSE
    ${x} =    IF    True    Set variable    Hello!
    Should Be Equal    ${x}    Hello!
    ${x} =    IF    False    Not run    ELSE IF    True    Set variable    World!
    Should Be Equal    ${x}    World!

Assign when no branch is run
    ${x} =    IF    False    Not run
    Should Be Equal    ${x}    ${None}
    ${x} =    IF    False    Not run    ELSE IF    False    Not run either
    Should Be Equal    ${x}    ${None}
    ${x}    @{y}    ${z} =    IF    False    Not run
    Should Be Equal    ${x}    ${None}
    Should Be Empty    ${y}
    Should Be Equal    ${z}    ${None}

Inside FOR
    [Documentation]    FAIL The end
    FOR    ${i}    IN    1    2    3
        IF    ${i} == 3    Fail    The end    ELSE    Log    ${i}
    END

Inside normal IF
    IF    ${True}
        Log   Hi
        IF    3==4    Fail    Should not be executed    ELSE    Log    Hello
        Log   Goodbye
    ELSE
        IF    True    Not run    ELSE    Not run
    END

In keyword
    [Documentation]    FAIL Expected failure
    Keyword with inline IFs

*** Keywords ***
Keyword with inline IFs
    ${x} =    IF    True    Convert to integer    42    ELSE    Not run
    IF    ${x} == 0      Not run    ELSE IF    $x == 42    Executed    ELSE    Not    run
    IF                False    Not run
    ...    ELSE IF    False    Not run
    ...    ELSE IF    False    Not run
    ...    ELSE IF    True     Failure
    ...    ELSE IF    False    Not run
    ...    ELSE IF    False    Not run
    ...    ELSE                Not run

Executed
    No operation

Failure
    Fail    Expected failure
