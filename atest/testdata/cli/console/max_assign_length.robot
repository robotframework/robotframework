*** Test Cases ***
10 chars
    ${value} =    Evaluate    '0123456789'

200 chars
    ${value} =    Evaluate    '0123456789' * 20

201 chars
    ${value} =    Evaluate    '0123456789' * 20 + '0'

1000 chars
    ${value} =    Evaluate    '0123456789' * 100

1001 chars
    ${value} =    Evaluate    '0123456789' * 100 + '0'

VAR
    VAR    ${value}    ${{'0123456789' * 100}}
