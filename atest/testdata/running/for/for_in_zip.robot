*** Variables ***
@{result}
@{LIST1}         a    b    c
@{LIST2}         x    y    z
@{LIST3}         ${1}    ${2}    ${3}
@{UNEVEN}        1    2    3    4    5

*** Test Cases ***
Two variables and lists
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${LIST2}
        @{result} =    Create List    @{result}    ${x}:${y}
    END
    Should Be True    ${result} == ['a:x', 'b:y', 'c:z']

Uneven lists cause deprecation warning by default
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${UNEVEN}
        @{result} =    Create List    @{result}    ${x}:${y}
    END
    Should Be True    ${result} == ['a:1', 'b:2', 'c:3']

Three variables and lists
    FOR    ${x}    ${y}    ${z}    IN ZIP    ${LIST1}    ${LIST2}    ${LIST3}
        @{result} =    Create List    @{result}    ${x}:${y}:${z}
    END
    Should Be True    ${result} == ['a:x:1', 'b:y:2', 'c:z:3']

Six variables and lists
    FOR    ${x}    ${y}    ${z}    ${å}    ${ä}    ${ö}    IN ZIP
    ...    ${LIST1}    ${LIST2}    ${LIST3}    ${LIST3}    ${LIST2}    ${LIST1}
        @{result} =    Create List    @{result}    ${x}:${y}:${z}:${å}:${ä}:${ö}
    END
    Should Be True    ${result} == ['a:x:1:1:x:a', 'b:y:2:2:y:b', 'c:z:3:3:z:c']

One variable and list
    [Documentation]    This isn't very useful...
    FOR    ${x}    IN ZIP    ${LIST1}
        @{result} =    Create List    @{result}    ${x}
    END
    Should Be True    ${result} == ['a', 'b', 'c']

One variable and two lists
    FOR    ${x}    IN ZIP    ${LIST1}    ${LIST2}
        @{result} =    Create List    @{result}    ${x}[0]:${x}[1]
    END
    Should Be True    ${result} == ['a:x', 'b:y', 'c:z']

One variable and six lists
    FOR    ${x}    IN ZIP    ${LIST1}    ${LIST2}    ${LIST3}
    ...                      ${LIST3}    ${LIST2}    ${LIST1}
        @{result} =    Create List    @{result}    ${{':'.join(str(i) for i in $x)}}
    END
    Should Be True    ${result} == ['a:x:1:1:x:a', 'b:y:2:2:y:b', 'c:z:3:3:z:c']

Other iterables
    [Documentation]    Handling non-lists. Should accept anything iterable
    ...                except strings and fail with a clear error message if
    ...                invalid data given.
    ${tuple} =    Evaluate    tuple('foo')
    ${generator} =    Evaluate    (i for i in range(10))
    FOR     ${x}    ${y}    IN ZIP    ${tuple}    ${generator}
        @{result}=    Create List    @{result}    ${x}:${y}
    END
    Should Be True    ${result} == ['f:0', 'o:1', 'o:2']

List variable containing iterables
    @{items} =    Create List    ${LIST1}    ${LIST2}    ${{('f', 'o', 'o')}}
    FOR    ${x}    ${y}    ${z}    IN ZIP    @{items}
        @{result}=    Create List    @{result}    ${x}:${y}:${z}
    END
    Should Be True    ${result} == ['a:x:f', 'b:y:o', 'c:z:o']

List variable with iterables can be empty
    FOR    ${x}    IN ZIP    @{EMPTY}
        Fail    Not executed
    END
    FOR    ${x}    ${y}    ${z}    IN ZIP    @{EMPTY}
        Fail    Not executed
    END
    Log    Executed!

Strict mode
    [Documentation]    FAIL    FOR IN ZIP items must have equal lengths in the STRICT mode, but lengths are 3, 3 and 5.
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${LIST2}    mode=STRICT
        @{result} =    Create List    @{result}    ${x}:${y}
    END
    Should Be True    ${result} == ['a:x', 'b:y', 'c:z']
    FOR    ${x}    ${y}    ${z}    IN ZIP    ${LIST1}    ${LIST2}    ${UNEVEN}    mode=strict
        Fail    Not executed
    END

Strict mode requires items to have length
    [Documentation]    FAIL    FOR IN ZIP items must have length in the STRICT mode, but item 2 does not.
    FOR    ${x}    ${y}    IN ZIP    ${LIST3}    ${{itertools.cycle(['A', 'B'])}}    mode=STRICT
        Fail    Not executed
    END

Shortest mode
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${LIST2}    mode=SHORTEST    fill=ignored
        @{result} =    Create List    @{result}    ${x}:${y}
    END
    Should Be True    ${result} == ['a:x', 'b:y', 'c:z']
    @{result} =    Create List
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${UNEVEN}    mode=${{'shortest'}}
        @{result} =    Create List    @{result}    ${x}:${y}
    END
    Should Be True    ${result} == ['a:1', 'b:2', 'c:3']

Shortest mode supports infinite iterators
    FOR    ${x}    ${y}    IN ZIP    ${LIST3}    ${{itertools.cycle(['A', 'B'])}}    mode=SHORTEST
        @{result} =    Create List    @{result}    ${x}:${y}
    END
    Should Be True    ${result} == ['1:A', '2:B', '3:A']

Longest mode
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${LIST2}    mode=LONGEST
        @{result} =    Create List    @{result}    ${x}:${y}
    END
    Should Be True    ${result} == ['a:x', 'b:y', 'c:z']
    @{result} =    Create List
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${UNEVEN}    mode=LoNgEsT
        @{result} =    Create List    @{result}    ${{($x, $y)}}
    END
    Should Be True    ${result} == [('a', '1'), ('b', '2'), ('c', '3'), (None, '4'), (None, '5')]

Longest mode with custom fill value
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${UNEVEN}    mode=longest    fill=?
        @{result} =    Create List    @{result}    ${{($x, $y)}}
    END
    Should Be True    ${result} == [('a', '1'), ('b', '2'), ('c', '3'), ('?', '4'), ('?', '5')]
    @{result} =    Create List
    FOR    ${x}    ${y}    ${z}    IN ZIP    ${{(1, 2)}}    ${LIST1}    ${{[1]}}    fill=${0}    mode=longest
        @{result} =    Create List    @{result}    ${{($x, $y, $z)}}
    END
    Should Be True    ${result} == [(1, 'a', 1), (2, 'b', 0), (0, 'c', 0)]

Invalid mode
    [Documentation]    FAIL    FOR option 'mode' does not accept value 'bad'. Valid values are 'STRICT', 'SHORTEST' and 'LONGEST'.
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${LIST2}    mode=bad
        Fail    Should not be executed
    END

Invalid mode from variable
    [Documentation]    FAIL    Invalid FOR IN ZIP mode: Value 'bad' is not accepted. Valid values are 'STRICT', 'SHORTEST' and 'LONGEST'.
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${LIST2}    mode=${{'bad'}}
        Fail    Should not be executed
    END

Config more than once 1
    [Documentation]    FAIL    FOR IN ZIP items must be list-like, but item 3 is string.
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${LIST2}    mode=longest    mode=shortest
        Fail    Should not be executed
    END

Config more than once 2
    [Documentation]    FAIL    FOR IN ZIP items must be list-like, but item 4 is string.
    FOR    ${items}    IN ZIP    ${LIST1}    ${LIST2}    ${LIST3}    fill=x    mode=longest    fill=y    fill=z
        Fail    Should not be executed
    END

Non-existing variable in mode
    [Documentation]    FAIL    Invalid FOR IN ZIP mode: Variable '\${bad}' not found.
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${LIST2}    mode=${bad}    fill=${ignored}
        Fail    Should not be executed
    END

Non-existing variable in fill value
    [Documentation]    FAIL    Invalid FOR IN ZIP fill value: Variable '\${bad}' not found.
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${LIST2}    mode=longest    fill=${bad}
        Fail    Should not be executed
    END

Not iterable value
    [Documentation]    FAIL    FOR IN ZIP items must be list-like, but item 2 is integer.
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${42}
        Fail    Should not be executed
    END

Strings are not considered iterables
    [Documentation]    FAIL    FOR IN ZIP items must be list-like, but item 3 is string.
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${LIST2}    not list
        Fail    Should not be executed
    END

Too few variables 1
    [Documentation]    FAIL
    ...    Number of FOR loop values should be multiple of its variables. \
    ...    Got 2 variables but 3 values.
    FOR    ${too}    ${few}    IN ZIP   ${LIST1}    ${LIST1}    ${LIST1}
        Fail    Should not be executed
    END

Too few variables 2
    [Documentation]    FAIL
    ...    Number of FOR loop values should be multiple of its variables. \
    ...    Got 3 variables but 4 values.
    @{items} =    Create List    ${LIST1}    ${LIST1}    ${LIST1}    ${LIST1}
    FOR    ${too}    ${few}    ${still}    IN ZIP   @{items}
        Fail    Should not be executed
    END

Too many variables 1
    [Documentation]    FAIL
    ...    Number of FOR loop values should be multiple of its variables. \
    ...    Got 3 variables but 2 values.
    FOR    ${too}    ${many}    ${variables}    IN ZIP    ${LIST1}    ${LIST2}
        Fail    Should not be executed
    END

Too many variables 2
    [Documentation]    FAIL
    ...    Number of FOR loop values should be multiple of its variables. \
    ...    Got 4 variables but 1 value.
    @{items} =    Create List    ${LIST1}
    FOR    ${too}    ${many}    ${variables}    ${again}    IN ZIP    @{items}
        Fail    Should not be executed
    END
