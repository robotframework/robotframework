*** Test Cases ***
Multiple conditions
    [Documentation]    FAIL    WHILE accepts only one condition, got 4 conditions 'Too', 'many', 'conditions' and '!'.
    WHILE    Too    many    conditions    !
        Fail    Not executed!
    END

Invalid condition
    [Documentation]    FAIL    Invalid WHILE loop condition: \
    ...    Evaluating expression 'bad' failed: NameError: name 'bad' is not defined nor importable as module
    WHILE    bad
        Fail    Not executed!
    END

Non-existing ${variable} in condition
    [Documentation]    FAIL    Invalid WHILE loop condition: \
    ...    Evaluating expression '\${bad} > 0' failed: Variable '\${bad}' not found.
    WHILE    ${bad} > 0
        Fail    Not executed!
    END

Non-existing $variable in condition
    [Documentation]    FAIL    Invalid WHILE loop condition: \
    ...    Evaluating expression '$bad > 0' failed: Variable '$bad' not found.
    WHILE    $bad > 0
        Fail    Not executed!
    END

Recommend $var syntax if invalid condition contains ${var}
    [Documentation]    FAIL    Invalid WHILE loop condition: \
    ...    Evaluating expression "x == 'x'" failed: NameError: name 'x' is not defined nor importable as module
    ...
    ...    Variables in the original expression "\${x} == 'x'" were resolved before the expression was evaluated. \
    ...    Try using "$x == 'x'" syntax to avoid that. See Evaluating Expressions appendix in Robot Framework User Guide for more details.
    ${x} =    Set Variable    x
    WHILE    ${x} == 'x'
        Fail    Not executed!
    END

Invalid condition on second round
    [Documentation]    FAIL    Invalid WHILE loop condition: \
    ...    Evaluating expression 'bad' failed: NameError: name 'bad' is not defined nor importable as module
    ...
    ...    Variables in the original expression '\${condition}' were resolved before the expression was evaluated. \
    ...    Try using '$condition' syntax to avoid that. See Evaluating Expressions appendix in Robot Framework User Guide for more details.
    ${condition} =    Set Variable    True
    WHILE    ${condition}
        IF    ${condition}
            ${condition} =    Set Variable    bad
        ELSE
            Fail    Not executed!
        END
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
    EXCEPT    Invalid WHILE loop condition: Evaluating expression 'bad' failed: NameError: name 'bad' is not defined nor importable as module
        No Operation
    END

Non-existing variable in condition causes normal error
    TRY
        WHILE    ${bad}
            Fail    Should not be run
        END
    EXCEPT    Invalid WHILE loop condition: Evaluating expression '\${bad}' failed: Variable '\${bad}' not found.
        No Operation
    END
