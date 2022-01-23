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
    [Documentation]    FAIL STARTS: Evaluating IF condition failed: Evaluating expression ''123'=123' failed: SyntaxError:
    IF    '123'=${123}
        Fail    Should not be run
    END

IF condition with non-existing variable
    [Documentation]    FAIL Evaluating IF condition failed: Variable '\${ooop}' not found.
    IF    ${ooop}
        Fail    Should not be run
    ELSE IF    ${not evaluated}
        Not run
    END

IF with invalid condition with ELSE
    [Documentation]    FAIL Evaluating IF condition failed: Evaluating expression 'ooops' failed: NameError: name 'ooops' is not defined nor importable as module
    IF    ooops
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    END

ELSE IF with invalid condition
    [Documentation]    FAIL STARTS: Evaluating ELSE IF condition failed: Evaluating expression '1/0' failed: ZeroDivisionError:
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

IF without END
    [Documentation]    FAIL    IF has no closing END.
    IF    ${True}
        Fail    Should not be run

Invalid END
    [Documentation]    FAIL    END does not accept arguments, got 'this', 'is' and 'invalid'.
    IF    True
        Fail    Should not be run
    END    this    is    invalid

IF with wrong case
    [Documentation]    FAIL    'If' is a reserved keyword. It must be an upper case 'IF' when used as a marker.
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
    [Documentation]    FAIL    ELSE IF cannot have more than one condition.
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
    [Documentation]    FAIL    Multiple ELSE branches.
    IF    'kuu' == 'maa'
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    END

ELSE IF after ELSE
    [Documentation]    FAIL    ELSE IF after ELSE.
    IF    'kuu' == 'maa'
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    ELSE IF    ${True}
        Log    hei
    END

Invalid IF inside FOR
    [Documentation]    FAIL    ELSE IF after ELSE.
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
    ...    - ELSE IF after ELSE.
    ...    - Multiple ELSE branches.
    ...    - IF has no closing END.
    ...    - ELSE IF cannot have more than one condition.
    ...    - ELSE IF branch cannot be empty.
    ...    - ELSE does not accept arguments, got 'oops'.
    ...    - ELSE branch cannot be empty.
    ...    - ELSE IF must have a condition.
    ...    - ELSE IF branch cannot be empty.
    ...    - ELSE branch cannot be empty.
    IF
    ELSE IF    too    many
    ELSE    oops
    ELSE IF
    ELSE
