*** Test Cases ***
Normal Text
    Should Be Equal    ${NORMAL TEXT}    Hello

Special Characters
    Should Be Equal    ${SPECIAL}    I'll take spam & eggs!!
    Should Be Equal    ${SPECIAL 2}    \${notvar}

No Colon In Variable
    Should Be Equal    ${NO COLON}    ${EMPTY}
