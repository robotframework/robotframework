*** Variables ***
@{result}
@{LIST1}         a    b    c
@{LIST2}         x    y    z
@{LIST3}         1    2    3    4    5

*** Test Cases ***
Two variables and lists
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${LIST2}
        @{result} =    Create List    @{result}    ${x}:${y}
    END
    Should Be True    ${result} == ['a:x', 'b:y', 'c:z']

Uneven lists
    [Documentation]    This will ignore any elements after the shortest
    ...                list ends, just like with Python's zip().
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${LIST3}
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
    FOR    ${x}    IN ZIP
    ...    ${LIST1}    ${LIST2}    ${LIST3}    ${LIST3}    ${LIST2}    ${LIST1}
        @{result} =    Create List    @{result}    ${{':'.join($x)}}
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
    ${tuple} =    Evaluate    tuple('foobar')
    @{items} =    Create List    ${LIST1}    ${LIST2}    ${tuple}
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

Not iterable value
    [Documentation]    FAIL    FOR IN ZIP items must all be list-like, got integer '42'.
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    ${42}
        Fail    This test case should die before running this.
    END

Strings are not considered iterables
    [Documentation]    FAIL    FOR IN ZIP items must all be list-like, got string 'not list'.
    FOR    ${x}    ${y}    IN ZIP    ${LIST1}    not list
        Fail    This test case should die before running this.
    END

Too few variables 1
    [Documentation]    FAIL
    ...    Number of FOR loop values should be multiple of its variables. \
    ...    Got 2 variables but 3 values.
    FOR    ${too}    ${few}    IN ZIP   ${LIST1}    ${LIST1}    ${LIST1}
        Fail    This test case should die before running this.
    END

Too few variables 2
    [Documentation]    FAIL
    ...    Number of FOR loop values should be multiple of its variables. \
    ...    Got 3 variables but 4 values.
    @{items} =    Create List    ${LIST1}    ${LIST1}    ${LIST1}    ${LIST1}
    FOR    ${too}    ${few}    ${still}    IN ZIP   @{items}
        Fail    This test case should die before running this.
    END

Too many variables 1
    [Documentation]    FAIL
    ...    Number of FOR loop values should be multiple of its variables. \
    ...    Got 3 variables but 2 values.
    FOR    ${too}    ${many}    ${variables}    IN ZIP    ${LIST1}    ${LIST2}
        Fail    This test case should die before running this.
    END

Too many variables 2
    [Documentation]    FAIL
    ...    Number of FOR loop values should be multiple of its variables. \
    ...    Got 4 variables but 1 value.
    @{items} =    Create List    ${LIST1}
    FOR    ${too}    ${many}    ${variables}    ${again}    IN ZIP    @{items}
        Fail    This test case should die before running this.
    END
