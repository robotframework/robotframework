*** Variables ***
@{result}
@{VALUES}         a    b    c    d

*** Test Cases ***
Index and item
    FOR    ${index}    ${item}    IN ENUMERATE    a    b    c    ${VALUES}[-1]
        Should Be True    isinstance($index, int)
        @{result} =     Create List    @{result}    ${index}:${item}
    END
    Should Be True    ${result} == ['0:a', '1:b', '2:c', '3:d']

Values from list variable
    FOR    ${index}    ${item}    IN ENUMERATE    @{VALUES}
        Should Be Equal    ${VALUES}[${index}]    ${item}
        @{result} =     Create List    @{result}    ${index}:${item}
    END
    Should Be True    ${result} == ['0:a', '1:b', '2:c', '3:d']

Start
    FOR    ${index}    ${item}    IN ENUMERATE    ${1}    ${2}    ${3}    ${4}    ${5}    start=1
        Should Be Equal    ${index}    ${item}
    END
    FOR    ${index}    ${item}    IN ENUMERATE    xxx    start\=xxx    start=${100}
        @{result} =     Create List    @{result}    ${index}:${item}
    END
    Should Be True    ${result} == ['100:xxx', '101:start=xxx']

Escape start
    FOR    ${index}    ${item}    IN ENUMERATE    start=ok    start\=ok
        Should Be Equal    ${item}    start=ok
        @{result} =     Create List    @{result}    ${index}
   END
    Should Be True    ${result} == [0, 1]

Invalid start
    [Documentation]    FAIL    Invalid FOR IN ENUMERATE start value: Value must be an integer, got 'invalid'.
    FOR    ${index}    ${item}    IN ENUMERATE    xxx    start=invalid
        Fail    Should not be executed
    END

Invalid variable in start
    [Documentation]    FAIL    Invalid FOR IN ENUMERATE start value: Variable '\${invalid}' not found.
    FOR    ${index}    ${item}    IN ENUMERATE    xxx    start=${invalid}
        Fail    Should not be executed
    END

Start multiple times
    FOR    ${index}    ${item}    IN ENUMERATE    start=1    start=2
        Should Be Equal    ${index}    ${2}
        Should Be Equal    ${item}     start=1
    END

Index and two items
    @{values} =    Create List    a    b    c    d    e    f
    FOR    ${i}    ${item1}    ${item2}    IN ENUMERATE    @{values}
        Should Be Equal    ${values}[${i * 2 + 0}]    ${item1}
        Should Be Equal    ${values}[${i * 2 + 1}]    ${item2}
        @{result} =     Create List    @{result}    ${i}:${item1}:${item2}
    END
    Should Be True    ${result} == ['0:a:b', '1:c:d', '2:e:f']

Index and five items
    @{values} =    Create List    a    b    c    d    e    f    g    h    i    j
    FOR    ${x}    ${i1}    ${i2}    ${i3}    ${i4}    ${i5}    IN ENUMERATE    @{values}
        Should Be Equal    ${values}[${x * 5 + 0}]    ${i1}
        Should Be Equal    ${values}[${x * 5 + 1}]    ${i2}
        Should Be Equal    ${values}[${x * 5 + 2}]    ${i3}
        Should Be Equal    ${values}[${x * 5 + 3}]    ${i4}
        Should Be Equal    ${values}[${x * 5 + 4}]    ${i5}
        @{result} =     Create List    @{result}    ${x}:${i1}:${i2}:${i3}:${i4}:${i5}
    END
    Should Be True    ${result} == ['0:a:b:c:d:e', '1:f:g:h:i:j']

One variable only
    FOR    ${item}    IN ENUMERATE    a    b    c
        Length Should Be    ${item}    2
        Should Be True    isinstance($item[0], int)
        @{result} =     Create List    @{result}    ${item}[0]:${item}[1]
    END
    Should Be True    ${result} == ['0:a', '1:b', '2:c']

Wrong number of variables
    [Documentation]    FAIL
    ...    Number of FOR IN ENUMERATE loop values should be multiple of its \
    ...    variables (excluding the index). Got 3 variables but 4 values.
    FOR    ${index}    ${item1}    ${item2}    ${item3}    IN ENUMERATE    @{VALUES}
        Fail    Should not be executed.
    END

No values
    [Documentation]    FAIL    FOR loop has no loop values.
    FOR    ${index}    ${item}    IN ENUMERATE
        Fail    Should not be executed.
    END

No values with start
    [Documentation]    FAIL    FOR loop has no loop values.
    FOR    ${index}    ${item}    IN ENUMERATE    start=0
        Fail    Should not be executed.
    END
