*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/passing_arguments.robot
Resource         atest_resource.robot

*** Test Cases ***
Command and arguments in system
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}
    ...    Starting process:\npython *script.py "my stdout" "my stderr"    pattern=true

Command and arguments in shell as separate arguments
    Check Test Case    ${TESTNAME}

Command and arguments in shell as single argument
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}
    ...    Starting process:\npython *script.py my args    pattern=true

Arguments are converted to strings automatically
    Check Test Case    ${TESTNAME}

Escaping equal sign
    Check Test Case    ${TESTNAME}

Unsupported kwargs cause error
    Check Test Case    ${TESTNAME}
