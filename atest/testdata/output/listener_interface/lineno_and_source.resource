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
