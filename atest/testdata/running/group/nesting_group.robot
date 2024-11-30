*** Test Cases ***
Test with Nested Groups
    GROUP
        ${var}    Set Variable    assignment
        GROUP     This Is A Named Group
            Should Be Equal    ${var}    assignment
        END
    END

Group with other control structure
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

Test With Not Executed Groups
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
    ELSE
        GROUP
            Fail    Shall be logged but NOT RUN
        END
    END