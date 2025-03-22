*** Variables ***
${INTEGER: int}    42
${LIST_OF_INTEGERS: list[int]}    [42, '1']
${NO_TYPE}    42

*** Test Cases ***
Variable Section Should Support Types
    Should Be Equal    ${INTEGER}    ${42}
    Should Be Equal    ${LIST_OF_INTEGERS}    ${{[42, 1]}}
    Should Be Equal    ${NO_TYPE}    42

VAR Should Support Types
    VAR    ${local: int|float}    123
    Should be equal    ${local}    ${123}
    VAR    ${local: list}    [1, "2", 3]
    Should be equal    ${local}    ${{[1, "2", 3]}}
