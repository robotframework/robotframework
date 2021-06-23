*** Variables ***
@{result}

*** Test Cases ***
Only stop
    FOR    ${i}    IN RANGE    100
        @{result} =    Create List    @{result}    ${i}
        Log    i: ${i}
    END
    Should Be True    ${result} == list(range(100))

Start and stop
    FOR    ${item}    IN RANGE    1    5
        @{result} =    Create List    @{result}    ${item}
    END
    Should Be True    ${result} == [1, 2, 3, 4]

Start, stop and step
    FOR    ${item}    IN RANGE    10    2    -3
        @{result} =    Create List    @{result}    ${item}
    END
    Should Be True    ${result} == [10, 7, 4]

Float stop 1
    FOR    ${item}    IN RANGE    3.14
        @{result} =    Create List    @{result}    ${item}
    END
    Should Be True    ${result} == [0, 1, 2, 3]

Float stop 2
    FOR    ${item}    IN RANGE    3.0
        @{result} =    Create List    @{result}    ${item}
    END
    Should Be True    ${result} == [0, 1, 2]

Float start and stop 1
    FOR    ${item}    IN RANGE    -1.5    1.5
        @{result} =    Create List    @{result}    ${item}
    END
    Should Be True    ${result} == [-1.5, -0.5, 0.5]

Float start and stop 2
    FOR    ${item}    IN RANGE    -1.5    1.500001
        @{result} =    Create List    @{result}    ${item}
    END
    Should Be True    ${result} == [-1.5, -0.5, 0.5, 1.5]

Float start, stop and step
    FOR    ${item}    IN RANGE    10.99    2.11    -3.04
        @{result} =    Create List    @{result}    ${item}
    END
    Should Be True    ${result} == [10.99, 7.95, 4.91]

Variables in arguments
    FOR    ${i}    IN RANGE    ${1}    ${3}
        @{result} =    Create List    @{result}    ${i}
    END
    Should Be True    ${result} == [1, 2]
    FOR    ${j}    IN RANGE    @{result}
        Should Be Equal    ${j}    ${1}
    END

Calculations
    FOR    ${i}    IN RANGE    ${3}-2    (3+${6})/3
        @{result} =    Create List    @{result}    ${i}
    END
    Should Be True    ${result} == [1, 2]

Calculations with floats
    FOR    ${i}    IN RANGE    3 + 0.14    1.5 - 2.5    2 * -1
        @{result} =    Create List    @{result}    ${i}
    END
    Should Be True    ${result} == [3.14, 1.14, -0.86]

Multiple variables
    FOR    ${a}    ${b}    ${c}    ${d}    ${e}    IN RANGE    5
        Should Be Equal    ${a}:${b}:${c}:${d}:${e}    0:1:2:3:4
    END
    Should Be Equal    ${a}:${b}:${c}:${d}:${e}    0:1:2:3:4
    FOR    ${i}    ${j}    ${k}    IN RANGE    -1    11
        @{result} =    Create List    @{result}    ${i}-${j}-${k}
    END
    Should Be True    ${result} == ['-1-0-1', '2-3-4', '5-6-7', '8-9-10']

Too many arguments
    [Documentation]    FAIL    FOR IN RANGE expected 1-3 values, got 4.
    FOR    ${i}    IN RANGE    1    2    3    4
        Fail    Not executed
    END
    Fail    Not executed

No arguments
    [Documentation]    FAIL    FOR loop has no loop values.
    FOR    ${i}    IN RANGE
        Fail    Not executed
    END
    Fail    Not executed

Non-number arguments 1
    [Documentation]    FAIL
    ...    STARTS: Converting FOR IN RANGE values failed: SyntaxError:
    FOR    ${i}    IN RANGE    not a number
        Fail    Not executed
    END
    Fail    Not executed

Non-number arguments 2
    [Documentation]    FAIL
    ...    STARTS: Converting FOR IN RANGE values failed: TypeError:
    FOR    ${i}    IN RANGE    0     ${NONE}
        Fail    Not executed
    END
    Fail    Not executed

Wrong number of variables
    [Documentation]    FAIL
    ...    Number of FOR loop values should be multiple of its variables. \
    ...    Got 2 variables but 11 values.
    FOR    ${x}    ${y}    IN RANGE    11
        Fail    Not executed
    END
    Fail    Not executed

Non-existing variables in arguments
    [Documentation]    FAIL    Variable '\@{non existing}' not found.
    FOR    ${i}    IN RANGE    @{non existing}
        Fail    Not executed
    END
    Fail    Not executed
