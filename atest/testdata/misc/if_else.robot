*** Test Cases ***
IF structure
    VAR    ${x}    value
    IF    '${x}' == 'wrong'
        Fail  not going here
    ELSE IF    '${x}' == 'value'
        Log   else if branch
    ELSE
        Fail  not going here
    END
