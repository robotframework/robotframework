*** Test Case ***
Markers should get note about case 1
    [Documentation]    FAIL 'For' is a reserved keyword. It must be an upper case 'FOR' when used as a marker.
    For    ${var}    IN    some    items
        Log    ${var}
    END

Markers should get note about case 2
    [Documentation]     FAIL 'If' is a reserved keyword. It must be an upper case 'IF' when used as a marker.
    ELSE    Log    ${message}

Markers should get note about case 3
    [Documentation]     FAIL 'Else' is a reserved keyword. It must be an upper case 'ELSE' when used as a marker.
    ELSE    Log    ${message}

Others should just be reserved 1
    [Documentation]    FAIL 'Continue' is a reserved keyword.
    Continue

Others should just be reserved 2
    [Documentation]    FAIL 'Return' is a reserved keyword.
    Return    ${something}

End gets extra note
    [Documentation]    FAIL 'End' is a reserved keyword. It must be an upper case 'END' and followed by an opening 'FOR' or 'IF' when used as a marker.
    END

Elif gets extra note
    [Documentation]    FAIL 'Elif' is a reserved keyword. The marker to use with 'IF' is 'ELSE IF'.
    ELIF

Reserved in user keyword
    [Documentation]    FAIL 'While' is a reserved keyword.
    User keyword with reserved keyword

*** Keyword ***
User keyword with reserved keyword
    While
