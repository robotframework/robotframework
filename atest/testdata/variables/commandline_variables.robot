*** Test Case ***
Normal Text
    Should Be Equal    ${NORMAL TEXT}    Hello

Escaped Text
    Should Be Equal    ${ESCAPED}    "I'll take spam & eggs!!"
    Should Be Equal    ${ESCAPED 2}    \${notvar}

No Colon In Variable
    Should Be Equal    ${NO COLON}    ${EMPTY}
