*** Test Cases ***
IF without condition
    [Documentation]    FAIL    IF must have a condition.
    IF
        Fail    Should not be run
    END

IF without condition with ELSE
    [Documentation]    FAIL    IF must have a condition.
    IF
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    END

IF with invalid condition
    [Documentation]    FAIL STARTS:     Invalid IF condition: Evaluating expression "'123'=123" failed: SyntaxError:
    IF    '123'=${123}
        Fail    Should not be run
    END

IF condition with non-existing ${variable}
    [Documentation]    FAIL    Invalid IF condition: Evaluating expression '\${ooop}' failed: Variable '\${ooop}' not found.
    IF    ${ooop}
        Fail    Should not be run
    ELSE IF    ${not evaluated}
        Not run
    END

IF condition with non-existing $variable
    [Documentation]    FAIL    Invalid IF condition: Evaluating expression '$ooop' failed: Variable '$ooop' not found.
    IF    $ooop
        Fail    Should not be run
    ELSE IF    $not_evaluated
        Not run
    END

IF with invalid condition with ELSE
    [Documentation]    FAIL     Invalid IF condition: \
    ...    Evaluating expression 'ooops' failed: NameError: name 'ooops' is not defined nor importable as module
    IF    ooops
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    END

ELSE IF with invalid condition
    [Documentation]    FAIL    STARTS: Invalid ELSE IF condition: Evaluating expression '1/0' failed: ZeroDivisionError:
    IF    False
        Fail    Should not be run
    ELSE IF    False
        Fail    Should not be run
    ELSE IF    1/0
        Fail    Should not be run
    ELSE IF    True
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    END

Recommend $var syntax if invalid condition contains ${var}
    [Documentation]    FAIL    Invalid IF condition: \
    ...    Evaluating expression "x == 'x'" failed: NameError: name 'x' is not defined nor importable as module
    ...
    ...    Variables in the original expression "\${x} == 'x'" were resolved before the expression was evaluated. \
    ...    Try using "$x == 'x'" syntax to avoid that. See Evaluating Expressions appendix in Robot Framework User Guide for more details.
    ${x} =    Set Variable    x
    IF    ${x} == 'x'
        Fail    Shouldn't be run
    END

IF without END
    [Documentation]    FAIL    IF must have closing END.
    IF    ${True}
        Fail    Should not be run

Invalid END
    [Documentation]    FAIL    END does not accept arguments, got 'this', 'is' and 'invalid'.
    IF    True
        Fail    Should not be run
    END    this    is    invalid

IF with wrong case
    [Documentation]    FAIL    No keyword with name 'if' found.
    if    ${True}
        Fail    Should not be run
    END

ELSE IF without condition
    [Documentation]    FAIL    ELSE IF must have a condition.
    IF    'mars' == 'mars'
        Fail    Should not be run
    ELSE IF
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    END

ELSE IF with multiple conditions
    [Documentation]    FAIL    ELSE IF cannot have more than one condition, got '\${False}', 'ooops' and '\${True}'.
    IF    'maa' == 'maa'
        Fail    Should not be run
    ELSE IF    ${False}    ooops    ${True}
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    END

ELSE with condition
    [Documentation]    FAIL    ELSE does not accept arguments, got '\${True}'.
    IF    'venus' != 'mars'
        Fail    Should not be run
    ELSE    ${True}
        Fail    Should not be run
    END

IF with empty body
    [Documentation]    FAIL    IF branch cannot be empty.
    IF    'jupiter' == 'saturnus'
    END

ELSE with empty body
    [Documentation]    FAIL    ELSE branch cannot be empty.
    IF    'kuu' == 'maa'
        Fail    Should not be run
    ELSE
    END

ELSE IF with empty body
    [Documentation]    FAIL    ELSE IF branch cannot be empty.
    IF    'mars' == 'maa'
        Fail    Should not be run
    ELSE IF    ${False}
    ELSE
        Fail    Should not be run
    END

ELSE after ELSE
    [Documentation]    FAIL    Only one ELSE allowed.
    IF    'kuu' == 'maa'
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    END

ELSE IF after ELSE
    [Documentation]    FAIL    ELSE IF not allowed after ELSE.
    IF    'kuu' == 'maa'
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    ELSE IF    ${True}
        Log    hei
    END

Dangling ELSE
    [Documentation]    FAIL    ELSE is not allowed in this context.
    ELSE

Dangling ELSE inside FOR
    [Documentation]    FAIL    ELSE is not allowed in this context.
    FOR    ${i}    IN    1    2
        ELSE
    END

Dangling ELSE inside WHILE
    [Documentation]    FAIL    ELSE is not allowed in this context.
    WHILE    ${True}
        ELSE
    END

Dangling ELSE IF
    [Documentation]    FAIL    ELSE IF is not allowed in this context.
    ELSE IF

Dangling ELSE IF inside FOR
    [Documentation]    FAIL    ELSE IF is not allowed in this context.
    FOR    ${i}    IN    1    2
        ELSE IF
    END

Dangling ELSE IF inside WHILE
    [Documentation]    FAIL    ELSE IF is not allowed in this context.
    WHILE    ${True}
        ELSE IF
    END

Dangling ELSE IF inside TRY
    [Documentation]    FAIL    ELSE IF is not allowed in this context.
    TRY
        Fail
    EXCEPT
        ELSE IF
    END

Invalid IF inside FOR
    [Documentation]    FAIL    ELSE IF not allowed after ELSE.
    FOR    ${value}    IN    1    2    3
        IF    ${value} == 1
            Fail    Should not be run
        ELSE
            Fail    Should not be run
        ELSE IF    ${value} == 3
            Fail    Should not be run
        END
    END

Multiple errors
    [Documentation]    FAIL
    ...    Multiple errors:
    ...    - IF must have a condition.
    ...    - IF branch cannot be empty.
    ...    - ELSE IF not allowed after ELSE.
    ...    - Only one ELSE allowed.
    ...    - IF must have closing END.
    ...    - ELSE IF cannot have more than one condition, got 'too' and 'many'.
    ...    - ELSE IF branch cannot be empty.
    ...    - ELSE does not accept arguments, got 'oops', 'i', 'did', 'it' and 'again'.
    ...    - ELSE branch cannot be empty.
    ...    - ELSE IF must have a condition.
    ...    - ELSE IF branch cannot be empty.
    ...    - ELSE branch cannot be empty.
    IF
    ELSE IF    too    many
    ELSE    oops    i    did    it    again
    ELSE IF
    ELSE

Invalid data causes syntax error
    [Documentation]    FAIL    IF branch cannot be empty.
    TRY
        IF    True
        END
    EXCEPT
        Fail    Syntax error cannot be caught
    END

Invalid condition causes normal error
    [Documentation]    FAIL    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Invalid IF condition: Evaluating expression 'bad in teardown' failed: NameError: name 'bad' is not defined nor importable as module
    ...
    ...    2) Should be run in teardown
    TRY
        IF    bad
            Fail    Should not be run
        END
    EXCEPT    Invalid IF condition: Evaluating expression 'bad' failed: NameError: name 'bad' is not defined nor importable as module
        No Operation
    END
    [Teardown]    Invalid condition

Non-existing variable in condition causes normal error
    [Documentation]    FAIL    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Invalid IF condition: Evaluating expression '\${oops}' failed: Variable '\${oops}' not found.
    ...
    ...    2) Should be run in teardown
    TRY
        IF    ${bad}
            Fail    Should not be run
        END
    EXCEPT    Invalid IF condition: Evaluating expression '\${bad}' failed: Variable '\${bad}' not found.
        No Operation
    END
    [Teardown]    Non-existing variable in condition

*** Keywords ***
Invalid condition
    IF    bad in teardown
        Fail    Should not be run
    ELSE
        Fail    Sould not be run either
    END
    Fail    Should be run in teardown

Non-existing variable in condition
    IF    ${oops}
        Fail    Should not be run
    END
    Fail    Should be run in teardown
