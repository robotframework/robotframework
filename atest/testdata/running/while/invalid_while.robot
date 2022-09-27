*** Test Cases ***
No condition
    [Documentation]    FAIL WHILE must have a condition.
    WHILE
        Fail    Not executed!
    END

Multiple conditions
    [Documentation]    FAIL WHILE cannot have more than one condition.
    WHILE    Too    many    !
        Fail    Not executed!
    END

Invalid condition
    [Documentation]    FAIL STARTS: Evaluating WHILE condition failed: Evaluating expression 'ooops!' failed: SyntaxError:
    WHILE    ooops!
        Fail    Not executed!
    END

Invalid condition on second round
    [Documentation]    FAIL Evaluating WHILE condition failed: Evaluating expression 'bad' failed: NameError: name 'bad' is not defined nor importable as module
    ${condition} =    Set Variable    True
    WHILE    ${condition}
        IF    ${condition}
            ${condition} =    Set Variable    bad
        ELSE
            Fail    Not executed!
        END
    END

Non-existing variable in condition
    [Documentation]    FAIL Evaluating WHILE condition failed: Variable '\${ooops}' not found.
    WHILE    ${ooops}
        Fail    Not executed!
    END

No body
    [Documentation]    FAIL WHILE loop cannot be empty.
    WHILE    True
    END

No END
    [Documentation]    FAIL WHILE loop must have closing END.
    WHILE    True
        Fail    Not executed!

Invalid data causes syntax error
    [Documentation]    FAIL WHILE loop cannot be empty.
    TRY
        WHILE    False
        END
    EXCEPT
        Fail    Syntax error cannot be caught
    END

Invalid condition causes normal error
    TRY
        WHILE    bad
            Fail    Should not be run
        END
    EXCEPT    Evaluating WHILE condition failed: Evaluating expression 'bad' failed: NameError: name 'bad' is not defined nor importable as module
        No Operation
    END

Non-existing variable in condition causes normal error
    TRY
        WHILE    ${bad}
            Fail    Should not be run
        END
    EXCEPT    Evaluating WHILE condition failed: Variable '\${bad}' not found.
        No Operation
    END
