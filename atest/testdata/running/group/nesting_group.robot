*** Test Cases ***
Nested
    GROUP
        ${var}    Set Variable    assignment
        GROUP     This Is A Named Group
            Should Be Equal    ${var}    assignment
        END
    END

With other control structures
    IF    True
        GROUP    Hello
            VAR    ${i}    ${0}
        END
        GROUP    With WHILE
            WHILE    $i < 2
                GROUP    Group1 Inside WHILE (${i})
                    Log    ${i}
                END
                GROUP    Group2 Inside WHILE
                    VAR    ${i}    ${i + 1}
                END
            END
            IF    $i != 2    Fail   Shall be logged but NOT RUN
        END
    END

In non-executed branch
    VAR    ${var}    value
    IF     True
        GROUP      GROUP in IF
            Should Be Equal    ${var}    value
            IF     True
                Log     IF in GROUP
            ELSE
                GROUP    GROUP in ELSE
                    Fail    Shall be logged but NOT RUN
                END
            END
        END
    ELSE IF    False
        GROUP    ${non_existing_variable_is_fine_here}
            Fail    Shall be logged but NOT RUN
        END
    ELSE
        # This possibly should be validated earlier so that the whole test would
        # fail for a syntax error without executing it.
        GROUP    Even empty GROUP is allowed
        END
    END
