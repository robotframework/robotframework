*** Test Cases ***
For
    [Documentation]    FAIL    'For' is a reserved keyword. It must be an upper case 'FOR' when used as a marker.
    For    ${x}    IN    invalid

Valid END after For
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 'For' is a reserved keyword. It must be an upper case 'FOR' when used as a marker.
    ...
    ...    2) 'End' is a reserved keyword. It must be an upper case 'END' and follow an opening 'FOR' or 'IF' when used as a marker.
    For    ${x}    IN    invalid
        Log    ${x}
    END

If
    [Documentation]    FAIL    'If' is a reserved keyword. It must be an upper case 'IF' when used as a marker.
    If    invalid

Else If
    [Documentation]    FAIL    'Else If' is a reserved keyword. It must be an upper case 'ELSE IF' and follow an opening 'IF' when used as a marker.
    Else If    invalid

Else
    [Documentation]    FAIL    'Else' is a reserved keyword. It must be an upper case 'ELSE' and follow an opening 'IF' when used as a marker.
    Else

Else inside valid IF
    [Documentation]    FAIL    'Else' is a reserved keyword. It must be an upper case 'ELSE' and follow an opening 'IF' when used as a marker.
    IF    False
        No operation
    Else
        No operation
    END

Else If inside valid IF
    [Documentation]    FAIL    'Else If' is a reserved keyword. It must be an upper case 'ELSE IF' and follow an opening 'IF' when used as a marker.
    IF    False
        No operation
    Else If    invalid
        No operation
    END

End
    [Documentation]    FAIL    'End' is a reserved keyword. It must be an upper case 'END' and follow an opening 'FOR' or 'IF' when used as a marker.
    End

End after valid FOR header
    [Documentation]    FAIL    FOR loop has no closing END.
    FOR    ${x}   IN    whatever
        Log    ${x}
    End

End after valid If header
    [Documentation]    FAIL    IF has no closing END.
    IF    True
        No operation
    End

Reserved inside FOR
    [Documentation]    FAIL    'If' is a reserved keyword. It must be an upper case 'IF' when used as a marker.
    FOR    ${x}    IN    whatever
        If    ${x}
    END

Reserved inside IF
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 'For' is a reserved keyword. It must be an upper case 'FOR' when used as a marker.
    ...
    ...    2) 'If' is a reserved keyword. It must be an upper case 'IF' when used as a marker.
    ...
    ...    3) 'End' is a reserved keyword. It must be an upper case 'END' and follow an opening 'FOR' or 'IF' when used as a marker.
    ...
    ...    4) 'Return' is a reserved keyword.
    ...
    ...    5) 'End' is a reserved keyword. It must be an upper case 'END' and follow an opening 'FOR' or 'IF' when used as a marker.
    IF    True
        For    ${x}    IN    invalid
            Log     ${x}
        END
        If    False
            No Operation
        END
        Return
    END
