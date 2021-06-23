*** Test Cases ***
IF without condition
    [Documentation]    FAIL    IF has no condition.
    IF
        Fail    Should not be run
    END

IF with ELSE without condition
    [Documentation]    FAIL    IF has no condition.
    IF
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    END

IF with many conditions
    [Documentation]    FAIL    IF has more than one condition.
    IF    '1' == '1'    '2' == '2'    '3' == '3'
        Fail    Should not be run
    END

IF with invalid condition
    [Documentation]    FAIL STARTS: Evaluating expression ''123'=123' failed: SyntaxError:
    IF    '123'=${123}
        Fail    Should not be run
    END

IF with ELSE with invalid condition
    [Documentation]    FAIL Evaluating expression 'ooops' failed: NameError: name 'ooops' is not defined nor importable as module
    IF    ooops
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    END

ELSE IF with invalid condition
    [Documentation]    FAIL STARTS: Evaluating expression '1/0' failed: ZeroDivisionError:
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
    [Documentation]    FAIL    END does not accept arguments.
    IF    True
        Fail    Should not be run
    END    this    is    invalid

IF with wrong case
    [Documentation]    FAIL    'If' is a reserved keyword. It must be an upper case 'IF' when used as a marker.
    if    ${True}
        Fail    Should not be run
    END

ELSE IF without condition
    [Documentation]    FAIL    ELSE IF has no condition.
    IF    'mars' == 'mars'
        Fail    Should not be run
    ELSE IF
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    END

ELSE IF with multiple conditions
    [Documentation]    FAIL    ELSE IF has more than one condition.
    IF    'maa' == 'maa'
        Fail    Should not be run
    ELSE IF    ${False}    ${True}
        Fail    Should not be run
    ELSE
        Fail    Should not be run
    END

ELSE with condition
    [Documentation]    FAIL    ELSE has condition.
    IF    'venus' != 'mars'
        Fail    Should not be run
    ELSE    ${True}
        Fail    Should not be run
    END

IF with empty body
    [Documentation]    FAIL    IF has empty body.
    IF    'jupiter' == 'saturnus'
    END

ELSE with empty body
    [Documentation]    FAIL    ELSE has empty body.
    IF    'kuu' == 'maa'
        Fail    Should not be run
    ELSE
    END

ELSE IF with empty body
    [Documentation]    FAIL    ELSE IF has empty body.
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
    ...    - IF has no condition.
    ...    - IF has empty body.
    ...    - ELSE IF after ELSE.
    ...    - Multiple ELSE branches.
    ...    - IF has no closing END.
    ...    - ELSE IF has more than one condition.
    ...    - ELSE IF has empty body.
    ...    - ELSE has condition.
    ...    - ELSE has empty body.
    ...    - ELSE IF has no condition.
    ...    - ELSE IF has empty body.
    ...    - ELSE has empty body.
    IF
    ELSE IF    too    many
    ELSE    oops
    ELSE IF
    ELSE
