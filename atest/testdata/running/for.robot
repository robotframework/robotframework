*** Settings ***
Variables         binary_list.py
Resource          old_for_in_resource.robot

*** Variables ***
@{NUMS}           1    2    3    4    5
@{RESULT}
${NO VALUES}      FOR loop has no loop values.
${NO KEYWORDS}    FOR loop contains no keywords.
${NO VARIABLES}   FOR loop has no loop variables.
${WRONG VALUES}   Number of FOR loop values should be multiple of its variables.

*** Test Cases ***
Simple loop
    Log    Not yet in FOR
    FOR    ${var}    IN    one    two
        Log    var: ${var}
    END
    Log    Not in FOR anymore

Variables in values
    FOR    ${num}    IN    @{NUMS}    ${6}
        Log    ${num}
        Log    Hello from for loop
        No Operation
        Run Keyword If    ${num} in [2,6]    Log    Presidential Candidate!    WARN
    END    # I can haz comments??!?

Indentation is not required
    ${string} =    Set Variable    START
    FOR    ${var}    IN    RoBoT    FRaMeWoRK
        ${string} =    Catenate    ${string}    ${var}
  ${string} =    Catenate    ${string}    ${var.title()}
                             ${string} =    Catenate    ${string}    ${var.upper()}
    ${string} =    Catenate    ${string}    ${var.lower()}
    END
    Should Be Equal    ${string}    START RoBoT Robot ROBOT robot FRaMeWoRK Framework FRAMEWORK framework

Values on multiple rows
    FOR    ${i}    IN    @{NUMS}    6    7    8
    ...    9    10
        Log    ${i}
    END
    Should Be Equal    ${i}    10

Keyword arguments on multiple rows
    FOR    ${var}    IN    one    two
        ${msg} =    Catenate    1    2    3    4
        ...    5    6    7    ${var}
        Log    ${msg}
        Should Be Equal    ${msg}    1 2 3 4 5 6 7 ${var}
    END

Multiple loops in one test
    FOR    ${x}    IN    foo    bar
        Log    In first loop with "${x}"
    END
    FOR    ${y}    IN    Hello, world!
        My UK 2    ${y}
    END
    Log    Outside loop
    FOR    ${z}    IN    a    b
        Log    Third loop
        No operation
        Log    Value: ${z}
    END
    Log    The End

Settings after FOR
    FOR    ${x}    IN    x
        ${x} =    Convert to Uppercase    ${x}
    END
    [Teardown]    Log    Teardown was found and e${x}ecuted.

Invalid END usage 1
    [Documentation]    FAIL    'End' is a reserved keyword.
    Log    No for loop here...
    END

Invalid END usage 2
    [Documentation]    FAIL    'End' is a reserved keyword.
    FOR    ${var}    IN    one    two
    \    Log    var: ${var}
    \    END

Invalid END usage 3
    [Documentation]    FAIL    'End' is a reserved keyword.
    FOR    ${var}    IN    one    two
    \    Log    var: ${var}
    End

Invalid END usage 4
    [Documentation]    FAIL    'End' is a reserved keyword.
    Invalid END usage in UK

FOR with empty body fails
    [Documentation]    FAIL    ${NO KEYWORDS}
    FOR    ${var}    IN    one    two
    END
    Fail    Not executed

FOR without END fails
    [Documentation]    FAIL    For loop has no closing 'END'.
    FOR    ${var}    IN    one    two
    Fail    Not executed

FOR without values fails
    [Documentation]    FAIL    ${NO VALUES}
    FOR    ${var}    IN
        Fail    Not executed
    END
    Fail    Not executed

Looping over empty list variable is OK
    FOR    ${var}    IN    @{EMPTY}
        Fail    Not executed
    END
    Variable Should Not Exist    ${var}

Other iterables
    ${generator} =    Evaluate    (i for i in range(5))
    ${tuple} =    Evaluate    (5, 6, 7, 8, 9)
    FOR     ${x}    IN    @{generator}    @{tuple}
        @{result} =    Create List    @{result}    ${x}
    END
    Should Be True    ${result} == list(range(10))

FOR Failing 1
    [Documentation]    FAIL    Here we fail!
    FOR    ${num}    IN    @{NUMS}
        Log    Hello before failing kw
        Fail    Here we fail!
        Fail    Not executed
    END
    Fail    Not executed

FOR Failing 2
    [Documentation]    FAIL    Failure with 4
    FOR    ${num}    IN    @{NUMS}
        Log    Before Check
        Should Not Be Equal    ${num}    4    Failure with ${num}    no values
        Log    After Check
    END
    Fail    Not executed

Loop with user keywords
    [Documentation]    FAIL    Fail outside for
    FOR    ${x}    IN    foo    bar
        My UK
        My UK 2    ${x}
    END
    Fail    Fail outside for

Loop with failures in user keywords
    [Documentation]    FAIL    Failure with 2
    FOR    ${num}    IN    @{NUMS}
        Failing UK    ${num}
    END
    Fail    Not executed

Loop in user keyword
    For In UK
    For In UK with Args    one    two    three    four

Nested loop in user keyword
    [Documentation]    FAIL    This ought to be enough
    Nested for In UK    foo    bar

Loop in test and user keyword
    [Documentation]    FAIL    This ought to be enough
    @{list} =    Create List    one    two
    FOR    ${item}    IN    @{list}
        For In UK
        For In UK with Args    @{list}
        Nested For In UK    @{list}
    END
    Fail    Not executed

Loop variables is available after loop
    Variable Should Not Exist    ${var}
    FOR    ${var}    IN    @{NUMS}
        Log    ${var}
    END
    Should Be Equal    ${var}    5
    FOR    ${var}    ${bar}    IN    foo    bar
        Log    ${var}
    END
    Should Be Equal    ${var}    foo
    Should Be Equal    ${bar}    bar

Assign inside loop
    FOR    ${x}    IN    Y    Z
        ${v1} =    Set Variable    v1
        ${v2}    ${v3} =    Create List    v2    v${x}
        @{list} =    Create List    ${v1}    ${v2}    ${v3}    ${x}
    END
    Should Be Equal    ${v1}    v1
    Should Be Equal    ${v2}    v2
    Should Be Equal    ${v3}    vZ
    Should Be True     ${list} == ['v1', 'v2', 'vZ', 'Z']

Invalid assign inside loop
    [Documentation]    FAIL
    ...    Cannot set variables: Expected list-like value, got string.
    FOR    ${i}    IN    1    2    3
        ${x}    ${y} =    Set Variable    Only one value
        Fail    Not executed
    END
    Fail    Not executed

No loop values
    [Documentation]    FAIL    ${NO VALUES}
    FOR    ${var}    IN
        Fail    Not Executed
    END
    Fail    Not Executed

Invalid loop variable 1
    [Documentation]    FAIL     Invalid FOR loop variable 'ooops'.
    FOR    ooops    IN    a    b    c
        Fail    Not Executed
    END
    Fail    Not Executed

Invalid loop variable 2
    [Documentation]    FAIL     Invalid FOR loop variable 'ooops'.
    FOR    ${var}    ooops    IN    a    b    c
        Fail    Not Executed
    END
    Fail    Not Executed

Invalid loop variable 3
    [Documentation]    FAIL     Invalid FOR loop variable '\@{ooops}'.
    FOR    @{ooops}    IN    a    b    c
        Fail    Not Executed
    END
    Fail    Not Executed

Invalid loop variable 4
    [Documentation]    FAIL     Invalid FOR loop variable '\&{ooops}'.
    FOR    &{ooops}    IN    a    b    c
        Fail    Not Executed
    END
    Fail    Not Executed

Invalid loop variable 5
    [Documentation]    FAIL    Invalid FOR loop variable '$var'.
    FOR    $var    IN    one    two
        Fail    Not Executed
    END
    Fail    Not Executed

Invalid loop variable 6
    [Documentation]    FAIL    Invalid FOR loop variable '\${not closed'.
    FOR    ${not closed    IN    one    two    three
        Fail    Not Executed
    END
    Fail    Not Executed

FOR without any paramenters
    [Documentation]    FAIL    ${NO VARIABLES}
    FOR
       Fail    Not Executed
    END
    Fail    Not Executed

FOR without variables
    [Documentation]    FAIL    Invalid FOR loop variable 'IN'.
    FOR    IN    one    two
        Fail    Not Executed
    END
    Fail    Not Executed

Loop with non-existing keyword
    [Documentation]    FAIL     No keyword with name 'Non Existing' found.
    FOR    ${i}    IN    1    2    3
        Non Existing
    END
    Fail    Not Executed

Loop with non-existing variable
    [Documentation]    FAIL     Variable '\${nonexisting}' not found.
    FOR    ${i}    IN    1    2    3
        Log    ${nonexisting}
    END
    Fail    Not Executed

Loop value with non-existing variable
    [Documentation]    FAIL     Variable '\${nonexisting}' not found.
    FOR    ${i}    IN    1    2    ${nonexisting}
            Fail    Not Executed
    END

Multiple loop variables
    FOR    ${x}    ${y}    IN
    ...      1       a
    ...      2       b
    ...      3       c
    ...      4       d
        Log    ${x}${y}
    END
    Should Be Equal    ${x}${y}    4d
    FOR    ${a}    ${b}    ${c}    ${d}    ${e}    IN
    ...    @{NUMS}    @{NUMS}
        Should Be Equal    ${a}${b}${c}${d}${e}    12345
    END
    Should Be Equal    ${a}${b}${c}${d}${e}    12345

Wrong number of loop variables 1
    [Documentation]    FAIL     ${WRONG VALUES} Got 3 variables but 5 values.
    FOR    ${a}    ${b}    ${c}    IN    @{NUMS}
        Fail    Not executed
    END
    Fail    Not executed

Wrong number of loop variables 2
    [Documentation]    FAIL     ${WRONG VALUES} Got 4 variables but 3 values.
    FOR    ${a}    ${b}    ${c}    ${d}    IN    a     b    c
        Fail    Not executed
    END
    Fail    Not executed

Cut long values in iteration name
    ${v10} =    Set Variable    0123456789
    ${v100} =    Evaluate    '${v10}' * 10
    ${v200} =    Evaluate    '${v100}' * 2
    ${v201} =    Set Variable    ${v200}1
    ${v300} =    Evaluate    '${v100}' * 3
    ${v10000} =    Evaluate    '${v100}' * 100
    FOR    ${var}    IN    ${v10}    ${v100}    ${v200}    ${v201}
    ...    ${v300}    ${v10000}
        Log    ${var}
    END
    FOR    ${var1}    ${var2}    ${var3}    IN    ${v10}    ${v100}
    ...    ${v200}    ${v201}    ${v300}    ${v10000}
        Log Many    ${var1}    ${var2}    ${var3}
    END
    Should Be Equal    ${var}    ${var3}    Sanity check

Characters that are illegal in XML
    FOR    ${var}    IN    @{ILLEGAL VALUES}
        Log    ${var}
    END

Header with colon is deprecated
    :FOR    ${x}    IN    a    b    c
        @{result} =    Create List    @{result}    ${x}
    END
    Should Be True    ${result} == ['a', 'b', 'c']

Header with colon is case and space insensitive
    : f O r    ${x}    IN    a    b    c
        @{result} =    Create List    @{result}    ${x}
    END
    Should Be True    ${result} == ['a', 'b', 'c']

Header can have many colons
    :::f:o:r:::    ${i}    IN RANGE    1    6
        @{result} =    Create List    @{result}    ${i}
    END
    Should Be True    ${result} == [1, 2, 3, 4, 5]

Invalid separator
    [Documentation]    FAIL    Invalid FOR loop variable 'IN INVALID'.
    FOR    ${i}    IN INVALID    Mr. Fancypants
        Fail    This shouldn't ever execute.
    END

Separator is case- and space-sensitive 1
    [Documentation]    FAIL Invalid FOR loop variable 'in'.
    FOR    ${x}    in    a    b    c
        Fail    Should not be executed
    END
    Fail    Should not be executed

Separator is case- and space-sensitive 2
    [Documentation]    FAIL Invalid FOR loop variable 'IN RANG E'.
    FOR    ${x}    IN RANG E    a    b    c
        Fail    Should not be executed
    END
    Fail    Should not be executed

Separator is case- and space-sensitive 3
    [Documentation]    FAIL Invalid FOR loop variable 'IN Enumerate'.
    FOR    ${x}    IN Enumerate    a    b    c
        Fail    Should not be executed
    END
    Fail    Should not be executed

Separator is case- and space-sensitive 4
    [Documentation]    FAIL Invalid FOR loop variable 'INZIP'.
    FOR    ${x}    INZIP    a    b    c
        Fail    Should not be executed
    END
    Fail    Should not be executed

Escaping with backslash is deprecated
    FOR    ${var}    IN    one    two
    \    Log    var: ${var}
    \    For in UK with backslashes    ${var}
    END
    Log    Between for loops
    FOR    ${var}    IN    one    two
    \    Log    var: ${var}
    \    For in UK with backslashes    ${var}
    END

END is not required when escaping with backslash
    FOR    ${var}    IN    one    two
    \    Log    var: ${var}
    \    For in UK with backslashes and without END    ${var}
    Log    Between for loops
    FOR    ${var}    IN    one    two
    \    Log    var: ${var}
    \    For in UK with backslashes and without END    ${var}

Header at the end of file
    [Documentation]    FAIL For loop has no closing 'END'.
    Header at the end of file

Old for loop in resource
    Old for loop in resource

*** Keywords ***
My UK
    No Operation
    Log    We are in My UK

My UK 2
    [Arguments]    ${arg}
    My UK
    Log    My UK 2 got argument "${arg}"
    My UK

Failing UK
    [Arguments]    ${num}
    My UK 2    ${num}
    Should Not Be Equal    ${num}    2    Failure with ${num}    no values

For In UK
    Log    Not for yet
    FOR    ${x}    IN    1    2
        Log    This is for with ${x}
        My UK
    END
    Log    Not for anymore

For In UK With Args
    [Arguments]    @{args}
    FOR    ${arg}    IN    @{args}
        My UK 2    ${arg}
    END
    Should Be Equal    ${arg}    ${args}[-1]
    FOR    ${arg}    IN    only once
        Log    This for loop is executed ${arg}
    END
    Should Be Equal    ${arg}    only once

Nested For In UK
    [Arguments]    @{args}
    FOR    ${arg}    IN    @{args}
        For In UK
        Nested for In UK 2    @{args}
    END

Nested For In UK 2
    [Arguments]    @{args}
    FOR    ${arg}    IN    @{args}
        For In UK
        Log    Got arg: ${arg}
    END
    Fail    This ought to be enough

For in UK with backslashes
    [Arguments]    ${arg}
    FOR    ${x}    IN    1    2
    \    No operation
    \    Log    ${arg}-${x}
    END

For in UK with backslashes and without END
    [Arguments]    ${arg}
    FOR    ${x}    IN    1    2
    \    No operation
    \    Log    ${arg}-${x}

Invalid END usage in UK
    END

Header at the end of file
    FOR    ${x}    IN    foo
