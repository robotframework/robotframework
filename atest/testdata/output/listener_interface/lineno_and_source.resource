*** Keywords ***
User Keyword In Resource
    No operation

FOR In Resource
    FOR    ${x}    IN    once
        Log    ${x}
    END

IF In Resource
    IF    True
        No Operation
    END

TRY In Resource
    TRY
        Log    Nothing to see here!
    FINALLY
        Log    Nothing interesting here either...
    END

Run Keyword in resource
    Run Keyword
    ...    Log    resource
