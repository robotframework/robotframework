*** Test Cases ***
Invalid condition
    [Documentation]    FAIL Evaluating IF condition failed: Evaluating expression 'ooops' failed: NameError: name 'ooops' is not defined nor importable as module
    IF    ooops    Not run    ELSE    Not run either

Condition with non-existing variable
    [Documentation]    FAIL Evaluating IF condition failed: Variable '\${ooops}' not found.
    IF    ${ooops}    Not run

Invalid condition with other error
    [Documentation]    FAIL ELSE branch cannot be empty.
    IF    bad    Not run    ELSE

Empty IF
    [Documentation]    FAIL Multiple errors:
    ...    - IF must have a condition.
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

IF followed by ELSE IF
    [Documentation]    FAIL STARTS: Evaluating IF condition failed: Evaluating expression 'ELSE IF' failed:
    IF    ELSE IF   False    Not run

IF followed by ELSE
    [Documentation]    FAIL Evaluating IF condition failed: Evaluating expression 'ELSE' failed: NameError: name 'ELSE' is not defined nor importable as module
    IF    ELSE    Not run

Empty ELSE IF 1
    [Documentation]    FAIL Multiple errors:
    ...    - ELSE IF must have a condition.
    ...    - ELSE IF branch cannot be empty.
    IF    False    Not run    ELSE IF

Empty ELSE IF 2
    [Documentation]    FAIL Evaluating ELSE IF condition failed: Evaluating expression 'ELSE' failed: NameError: name 'ELSE' is not defined nor importable as module
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
    IF    True     No operation    ELSE    Log    END
    IF    False    Not run         ELSE    No operation    END

Invalid END after inline header
    [Documentation]    FAIL 'End' is a reserved keyword. It must be an upper case 'END' when used as a marker to close a block.
    IF    True    Log    Executed inside inline IF
        Log   Executed outside IF
    END

Assign in IF branch
    [Documentation]    FAIL Inline IF branches cannot contain assignments.
    IF    False    ${x} =    Whatever

Assign in ELSE IF branch
    [Documentation]    FAIL Inline IF branches cannot contain assignments.
    IF    False    Keyword    ELSE IF   False    ${x} =    Whatever

Assign in ELSE branch
    [Documentation]    FAIL Inline IF branches cannot contain assignments.
    IF    False    Keyword    ELSE    ${x} =    Whatever

Invalid assign mark usage
    [Documentation]    FAIL Assign mark '=' can be used only with the last variable.
    ${x} =    ${y}    IF    True    Create list    x    y

Too many list variables in assign
    [Documentation]    FAIL Assignment can contain only one list variable.
    @{x}    @{y} =    IF    True    Create list    x    y    ELSE    Not run

Invalid number of variables in assign
    [Documentation]    FAIL Cannot set variables: Expected 2 return values, got 3.
    ${x}    ${y} =    IF    False    Create list    x    y     ELSE    Create list    x    y    z

Invalid value for list assign
    [Documentation]    FAIL Cannot set variable '\@{x}': Expected list-like value, got string.
    @{x} =    IF    True    Set variable    String is not list

Invalid value for dict assign
    [Documentation]    FAIL Cannot set variable '\&{x}': Expected dictionary-like value, got string.
    &{x} =    IF    False    Not run    ELSE    Set variable    String is not dict either

Assign when IF branch is empty
    [Documentation]    FAIL IF branch cannot be empty.
    ${x} =    IF    False

Assign when ELSE IF branch is empty
    [Documentation]    FAIL ELSE IF branch cannot be empty.
    ${x} =    IF    True    Not run    ELSE IF    True

Assign when ELSE branch is empty
    [Documentation]    FAIL ELSE branch cannot be empty.
    ${x} =    IF    True    Not run    ELSE

Assign with RETURN
    [Documentation]    FAIL Inline IF with assignment can only contain keyword calls.
    Assign with RETURN

*** Keywords ***
Assign with RETURN
    ${x} =    IF    False    RETURN    ELSE    Not run
