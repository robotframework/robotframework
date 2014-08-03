*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/passing_arguments.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Just command
    Check Test Case    ${TESTNAME}

Command and arguments
    Check Test Case    ${TESTNAME}

Escaping equal sign
    Check Test Case    ${TESTNAME}

Unsupported kwargs cause error
    Check Test Case    ${TESTNAME}
