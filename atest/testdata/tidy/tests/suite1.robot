*** Variables ***
${MyVar}          a value

*** Test Cases ***
My Test Case
    [Documentation]    This is an example test case
    Log    ${MyVar} and ${CURDIR}

Another Test
    My Keyword

*** Keywords ***
My Keyword
    FOR    ${i}    IN RANGE   10
        Log    ${i}
    END
