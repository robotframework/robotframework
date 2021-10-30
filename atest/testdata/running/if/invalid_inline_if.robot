*** Test Cases ***
Invalid condition
    [Documentation]    FAIL Evaluating expression 'ooops' failed: NameError: name 'ooops' is not defined nor importable as module
    IF    ooops    Not run    ELSE    Not run either

Empty IF
    [Documentation]    FAIL Multiple errors:
    ...    - IF has no condition.
    ...    - IF branch cannot be empty.
    ...    - IF has no closing END.
    IF

IF without branch
    [Documentation]    FAIL Multiple errors:
    ...    - IF branch cannot be empty.
    ...    - IF has no closing END.
    IF    True

IF without branch with ELSE IF
    [Documentation]    FAIL IF branch cannot be empty.
    IF    True    ELSE IF    True    Not run

IF without branch with ELSE
    [Documentation]    FAIL IF branch cannot be empty.
    IF    True    ELSE    Not run

IF follewed by ELSE IF
    [Documentation]    FAIL STARTS: Evaluating expression 'ELSE IF' failed:
    IF    ELSE IF   False    Not run

IF follewed by ELSE
    [Documentation]    FAIL Evaluating expression 'ELSE' failed: NameError: name 'ELSE' is not defined nor importable as module
    IF    ELSE    Not run

Empty ELSE IF 1
    [Documentation]    FAIL Multiple errors:
    ...    - ELSE IF has no condition.
    ...    - ELSE IF branch cannot be empty.
    IF    False    Not run    ELSE IF

Empty ELSE IF 2
    [Documentation]    FAIL Evaluating expression 'ELSE' failed: NameError: name 'ELSE' is not defined nor importable as module
    IF    False    Not run    ELSE IF    ELSE    Not run

ELSE IF without branch 1
    [Documentation]   FAIL ELSE IF branch cannot be empty.
    IF    False    Not run    ELSE IF    False

ELSE IF without branch 2
    [Documentation]   FAIL ELSE IF branch cannot be empty.
    IF    False    Not run    ELSE IF    False    ELSE    Not run

Empty ELSE
    [Documentation]    FAIL ELSE branch cannot be empty.
    IF    True    Not run    ELSE IF    True    Not run    ELSE

ELSE IF after ELSE 1
    [Documentation]    FAIL ELSE IF after ELSE.
    IF    True    Not run    ELSE    Not run    ELSE IF    True    Not run

ELSE IF after ELSE 2
    [Documentation]    FAIL ELSE IF after ELSE.
    IF    True    Not run    ELSE    Not run    ELSE IF    True    Not run     ELSE IF    True    Not run

Multiple ELSEs 1
    [Documentation]    FAIL Multiple ELSE branches.
    IF    True    Not run    ELSE    Not run    ELSE    Not run

Multiple ELSEs 2
    [Documentation]    FAIL Multiple ELSE branches.
    IF    True    Not run    ELSE    Not run    ELSE    Not run    ELSE    Not run

Nested IF 1
    [Documentation]    FAIL Inline IF cannot be nested.
    IF    True    IF    True    Not run

Nested IF 2
    [Documentation]    FAIL Inline IF cannot be nested.
    IF    True    Not run    ELSE    IF    True    Not run

Nested IF 3
    [Documentation]    FAIL Inline IF cannot be nested.
    IF                True    IF    True    Not run
    ...    ELSE IF    True    IF    True    Not run
    ...    ELSE               IF    True    Not run

Nested FOR
    [Documentation]    FAIL 'For' is a reserved keyword. It must be an upper case 'FOR' when used as a marker.
    IF    True    FOR    ${x}    IN    @{stuff}

Unnecessary END
    [Documentation]    FAIL Keyword 'BuiltIn.No Operation' expected 0 arguments, got 1.
    IF    False    Not run    ELSE    No operation    END

Assign in IF branch
    [Documentation]    FAIL Inline IF branch cannot have an assignment.
    IF    False    ${x} =    Whatever

Assign in ELSE IF branch
    [Documentation]    FAIL Inline ELSE IF branch cannot have an assignment.
    IF    False    Keyword    ELSE IF   False    ${x} =    Whatever

Assign in ELSE branch
    [Documentation]    FAIL Inline ELSE branch cannot have an assignment.
    IF    False    Keyword    ELSE    ${x} =    Whatever

Invalid assing mark usage
    [Documentation]    FAIL Assign mark '=' can be used only with the last variable.
    ${x} =    ${y}    IF    True    Create list    x    y

Too many list variables in assign
    [Documentation]    FAIL Assignment can contain only one list variable.
    @{x}    @{y} =    IF    True    Create list    x    y

Invalid number of variables in assign
    [Documentation]    FAIL Cannot set variables: Expected 2 return values, got 3.
    ${x}    ${y} =    IF    False    Create list    x    y     ELSE    Create list    x    y    z

Invalid value for list assign
    [Documentation]    FAIL Cannot set variable '\@{x}': Expected list-like value, got string.
    @{x} =    IF    True    Set variable    String is not list

Invalid value for dict assign
    [Documentation]    FAIL Cannot set variable '\&{x}': Expected dictionary-like value, got string.
    &{x} =    IF    False    Not run    ELSE    Set variable    String is not dict either
