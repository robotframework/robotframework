*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/passing_arguments.robot
Resource         atest_resource.robot

*** Test Cases ***
Command and arguments in system
    Check Test Case    ${TESTNAME}

Command and arguments in shell as separate arguments
    Check Test Case    ${TESTNAME}

Command and arguments in shell as single argument
    Check Test Case    ${TESTNAME}

Arguments are converted to strings automatically
    Check Test Case    ${TESTNAME}

Escaping equal sign
    Check Test Case    ${TESTNAME}

Unsupported kwargs cause error
    Check Test Case    ${TESTNAME}
