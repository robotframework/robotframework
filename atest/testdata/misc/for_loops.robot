*** Variables ***
@{ANIMALS}       cat      dog      horse

*** Test Cases ***
FOR
    FOR    ${pet}    IN    @{ANIMALS}
        Log    ${pet}
    END

FOR IN RANGE
    FOR    ${i}    IN RANGE    10
        Log    ${i}
        IF    ${i} == 9    BREAK
        CONTINUE
        Not executed!
    END

FOR IN ENUMERATE
    FOR    ${index}    ${element}    IN ENUMERATE    @{ANIMALS}    start=1
        Log    ${index}: ${element}
    END

FOR IN ZIP
    VAR    @{finnish}       kissa    koira    hevonen
    FOR    ${en}    ${fi}    IN ZIP    ${ANIMALS}    ${finnish}    mode=LONGEST    fill=-
        Log    ${en} is ${fi} in Finnish
    END
