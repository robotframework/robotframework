*** Settings ***
Test Template       Should Be Equal

*** Variables ***
${VARIABLE}         Variable content
${SAME VARIABLE}    Variable content

*** Test Cases ***
Using Normal Keyword Is Not Possible With Template
    Fail    Fail

Default Template
    [Documentation]    FAIL    Something != Different
    Same         Same
    42           42
    Something    Different

Continue On Failure
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 42 != 43
    ...
    ...    2) Something != Different
    Same         Same
    42           43
    Something    Different

Overriding Default Template In Test
    [Documentation]    FAIL    Same == Same
    [Template]    Should Not Be Equal
    Same         Same
    42           43
    Something    Different

Overriding Default Template In Test With Empty Value
    [Documentation]    FAIL    This should be executed as normal keyword
    [Template]
    Fail    This should be executed as normal keyword

Overriding Default Template In Test With NONE Value
    [Documentation]    FAIL    This should be executed as normal keyword
    [Template]    NoNe
    Fail    This should be executed as normal keyword

Template With Variables
    [Template]    Expect Exactly Two Args
    ${VARIABLE}    ${VARIABLE}

Template With \@{EMPTY} Variable
    [Template]    Template With Default Parameters
    @{EMPTY}

Template With Variables And Keyword Name
    [Template]    Expect Exactly Three Args
    ${SAME VARIABLE}    Variable content    ${VARIABLE}

Template With Variable And Assign Mark (=)
    [Documentation]    FAIL    1= != 2=
    [Template]    Expect Exactly Two Args
    ${42} =    42 =
    ${42}=     42=
    ${1}=      ${2}=

Named Arguments
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) foo != default
    ...
    ...    2) default != fool
    [Template]    Template With Default Parameters
    first=foo
    foo            second=foo
    first=foo      second=foo
    second=foo     first=foo
    second=fool

Varargs
    [Documentation]    FAIL    This != will fail
    [Template]    Template With Varargs
    ${EMPTY}
    Hello                   Hello
    Hello world             Hello    world
    1 2 3 4 5 6 7 8 9 10    1    2    3    4    5    6    7    8    9    10
    This                    will    fail

Empty Values
    [Template]  Expect Exactly Two Args
    \           \
    ${EMPTY}    \

Template With FOR Loop
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) This != Fails
    ...
    ...    2) This != Fails
    ...
    ...    3) Same != Different
    ...
    ...    4) This != Fails
    ...
    ...    5) Samething != Different
    Same    Same
    FOR    ${item}    IN    Same    Different    Same
        Same    Same
        This    Fails
        Same    ${item}
    END
    Samething    Different

Template With FOR Loop Containing Variables
    [Documentation]    FAIL    Variable content != 42
    [Tags]    42
    FOR    ${item}    IN    ${VARIABLE}    ${SAME VARIABLE}    @{TEST TAGS}
        ${VARIABLE}    ${item}
    END

Template With FOR IN RANGE Loop
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 0 != 1
    ...
    ...    2) 0 != 2
    ...
    ...    3) 0 != 3
    ...
    ...    4) 0 != 4
    FOR    ${index}    IN RANGE    5
        ${0}    ${index}
    END

Nested FOR
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) a != b
    ...
    ...    2) b != a
    ...
    ...    3) b != a
    ...
    ...    4) c != a
    ...
    ...    5) c != b
    ...
    ...    6) c != a
    FOR    ${x}    IN    a    b    c
        FOR    ${y}    IN    a    b
            ${x}    ${y}
        END
        ${x}    A    ignore_case=True
    END

Invalid FOR
    [Documentation]    FAIL
    ...    Multiple errors:
    ...    - FOR loop has no loop values.
    ...    - FOR loop must have closing END.
    FOR    ${x}    IN
        ${x}    not run

Template With IF
    IF    False
        Not     Run
    ELSE IF    False
        Run     Not
    ELSE
        Same    Same
    END

Template With IF Failing
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Not != Same
    ...
    ...    2) Same != Not
    IF    True
        Not     Same
    END
    IF    False
        Not     Run
    ELSE IF    True
        Same    Not
    ELSE
        Not     Run
    END

Invalid IF
    [Documentation]    FAIL
    ...    Multiple errors:
    ...    - IF must have a condition.
    ...    - IF must have closing END.
    IF
        Not    Run

FOR and IF
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) b != wrong
    ...
    ...    2) d != bad
    FOR    ${x}    IN    a    b    c    d
        IF    '${x}' == 'a'
            ${x}    a
        ELSE IF    '${x}' == 'b'
            ${x}    wrong
        ELSE IF    '${x}' == 'c'
            ${x}    c
        ELSE
            ${x}    bad
        END
    END

User Keywords Should Not Be Continued On Failure
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Expected failure
    ...
    ...    2) Second expected failure
    [Template]    Failing Uk With Multiple Fails
    Expected failure
    Second expected failure

Commented Rows With Test Template
    [Documentation]    FAIL   Sanity != Check
    # My comment
    Same      Same     # Another comment
    # Yet another comment
    42        42
    Sanity    Check    # with comment
    # And one final comment here

Templates with Run Keyword
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) First failure
    ...
    ...    2) No keyword with name 'Variable content =' found.
    [Template]    Run Keyword
    Should be equal    42    42
    Fail    First failure
    Expect exactly three args    xxx    xxx    xxx
    ${VARIABLE} =    Set variable    this doesn't work

Templates with continuable failures
    [Documentation]  FAIL
    ...    Several failures occurred:
    ...
    ...    1) Continuable 1
    ...
    ...    2) Continuable 1
    ...
    ...    3) Continuable 2
    ...
    ...    4) Continuable 1
    ...
    ...    5) Continuable 2
    ...
    ...    6) Continuable 3
    ...
    ...    7) Continuable 1
    ...
    ...    8) Continuable 2
    ...
    ...    9) Continuable 3
    ...
    ...    10) Continuable 4
    ...
    ...    11) Continuable 5
    [Template]  Continuable failures
    1
    2
    3
    5

Templated test ends after test timeout
    [Documentation]    FAIL    Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1 seconds
    [Template]    Sleep
    0.3 seconds
    0.2 seconds
    0.1 seconds

Templated test with for loop ends after test timeout
    [Documentation]    FAIL    Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1 seconds
    [Template]    Sleep
    FOR    ${i}    IN RANGE    10
        0.05 seconds
    END

Templated test continues after keyword timeout
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Failing after 0s sleep and before 10s timeout.
    ...
    ...    2) Keyword timeout 1 millisecond exceeded.
    ...
    ...    3) Failing after 0.01s sleep and before 1min timeout.
    ...
    ...    4) Keyword timeout 2 milliseconds exceeded.
    [Template]    Template with timeout
    sleep=0s
    sleep=1s      timeout=0.001s
    sleep=0.01s   timeout=1min
    sleep=2s      timeout=0.002s

Templated test with for loop continues after keyword timeout
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Keyword timeout 1 millisecond exceeded.
    ...
    ...    2) Failing after 0s sleep and before 15s timeout.
    [Template]    Template with timeout
    FOR    ${sleep}    ${timeout}    IN    1    0.001    0    15
        ${sleep}s    ${timeout}s
    END

Templated test ends after syntax errors
    [Documentation]    FAIL   IF must have closing END.
    [Template]    Syntax Error
    fails here
    not run

Templated test continues after non-syntax errors
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Variable '\${this does not exist}' not found.
    ...
    ...    2) Keyword 'BuiltIn.Should Be Equal' expected 2 to 8 arguments, got 1.
    ...
    ...    3) Compared and not equal != Fails
    ${this does not exist}    ${this does not exist either}
    Too few args
    Compared and equal        Compared and equal
    Compared and not equal    Fails

Templates and fatal errors 1
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) First error
    ...
    ...    2) Second error is fatal and should stop execution
    [Template]  Run Keyword
    Fail    First error
    Fatal Error    Second error is fatal and should stop execution
    Fail    This should not be executed

Templates and fatal errors 2
    [Documentation]    FAIL    Test execution stopped due to a fatal error.
    Fail    This should not be executed

*** Keywords ***
Template With Default Parameters
    [Arguments]    ${first}=default    ${second}=default
    Should Be Equal    ${first}    ${second}

Template With Varargs
    [Arguments]    ${first}    @{second}
    ${second} =    Catenate    @{second}
    Should Be Equal    ${first}    ${second}

Expect Exactly Two Args
    [Arguments]    ${a1}    ${a2}
    Should Be Equal    ${a1}    ${a2}

Expect Exactly Three Args
    [Arguments]    ${a1}    ${a2}    ${a3}
    Should Be Equal    ${a1}    ${a2}
    Should Be Equal    ${a1}    ${a3}

Failing Uk With Multiple Fails
    [Arguments]    ${msg}
    Fail    ${msg}
    Fail    This should not be executed

Continuable failures
    [Arguments]    ${count}
    FOR    ${i}    IN RANGE    ${count}
        Run keyword and continue on failure    Fail    Continuable ${i+1}
    END

Template with timeout
    [Arguments]    ${sleep}=0s    ${timeout}=10s
    [Timeout]    ${timeout}
    Sleep    ${sleep}
    Fail    Failing after ${sleep} sleep and before ${timeout} timeout.

Syntax Error
    [Arguments]    ${arg}
    IF    ${arg}
        Fail    Should not be run due to END missing.
