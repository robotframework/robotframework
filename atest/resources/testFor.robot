*** Setting ***
Resource          atest_resource.robot


*** Test Cases ***
Example
    FOR    ${x}    IN    a    b    c
        Log To Console    ${x}
        BREAK
    END