*** Variables ***
${NAME}        Name
${VARIABLE}    Variable
@{MY LIST}     My    List
&{MY DICT}     key=value

*** Test Cases ***
Test Case ${NAME} With ${VARIABLE} 
    Should Be Equal    ${TESTNAME}    Test Case ${NAME} With ${VARIABLE}

Test Case ${NAME} With ${MY LIST} 
    Should Be Equal    ${TESTNAME}    Test Case ${NAME} With ${MY LIST}

Test Case ${NAME} With ${MY DICT} 
    Should Be Equal    ${TESTNAME}    Test Case ${NAME} With ${MY DICT}

Test Case ${NAME} With ${UNKONW VARIABLE}
    Should Be Equal    ${TESTNAME}    Test Case ${NAME} With \${UNKONW VARIABLE}
