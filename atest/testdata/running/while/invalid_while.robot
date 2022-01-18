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
    [Documentation]    FAIL STARTS: Evaluating WHILE loop condition failed: Evaluating expression 'ooops!' failed: SyntaxError:
    WHILE    ooops!
        Fail    Not executed!
    END

Non-existing variable in condition
    [Documentation]    FAIL Evaluating WHILE loop condition failed: Variable '\${ooops}' not found.
    WHILE    ${ooops}
        Fail    Not executed!
    END

No body
    [Documentation]    FAIL WHILE loop has empty body.
    WHILE    True
    END

No END
    [Documentation]    FAIL WHILE loop has no closing END.
    WHILE    True
        Fail    Not executed!
