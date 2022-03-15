*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    variables/builtin_variables.robot
Resource        atest_resource.robot

*** Test Cases ***
Integer Variables
    Check Test Case    ${TESTNAME}

Integer Variables With Base
    Check Test Case    ${TESTNAME}

Float Variables
    Check Test Case    ${TESTNAME}

Boolean Variables
    Check Test Case    ${TESTNAME}

\${None} And \${null}
    Check Test Case    ${TESTNAME}

\${SPACE}
    Check Test Case    ${TESTNAME}

\${EMPTY}
    Check Test Case    ${TESTNAME}

\@{EMPTY}
    Check Test Case    ${TESTNAME}

\&{EMPTY}
    Check Test Case    ${TESTNAME}

\@{EMPTY} and \&{EMPTY} cannot be modified
    Check Test Case    ${TESTNAME}

\${/}
    Check Test Case    ${TESTNAME}

\${:}
    Check Test Case    ${TESTNAME}

\${\\n}
    Check Test Case    ${TESTNAME}

\${TEMPDIR}
    Check Test Case    ${TESTNAME}

\${EXECDIR}
    Check Test Case    ${TESTNAME}

$CURDIR
    Check Test Case    ${TESTNAME}

\${LOG LEVEL}
    Check Test Case    ${TESTNAME}
