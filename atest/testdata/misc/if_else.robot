*** Test Cases ***
IF structure
    IF    'IF' == 'WRONG'
        Fail  not going here
    ELSE IF    'ELSE IF' == 'ELSE IF'
        Log   else if branch
    ELSE
        Fail  not going here
    END
