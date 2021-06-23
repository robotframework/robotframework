*** Variables ***
${NAME}        Name
${VARIABLE}    Variable

*** Test Cases ***
Test Case "${NAME}" With "${VARIABLE}"
    Should Be Equal    ${TESTNAME}    Test Case "Name" With "Variable"

Test Case "${2}" With "@{EMPTY}"
    Should Be Equal    ${TESTNAME}    Test Case "2" With "[]"

Test Case "${NAME}" With "${UNKNOWN VARIABLE}"
    Should Be Equal    ${TESTNAME}    Test Case "Name" With "\${UNKNOWN VARIABLE}"
