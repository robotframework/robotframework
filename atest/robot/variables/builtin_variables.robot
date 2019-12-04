*** Settings ***
Suite Setup     Run Tests  --variable FALSE:CLI --variable 77:CLI  variables/builtin_variables.robot
Resource        atest_resource.robot

*** Test Cases ***
Integer Variables
    Check Test Case  ${TESTNAME}

Integer Variables With Base
    Check Test Case  ${TESTNAME}

Float Variables
    Check Test Case  ${TESTNAME}

Boolean Variables
    Check Test Case  ${TESTNAME}

\${None} And \${null}
    Check Test Case  ${TESTNAME}

\${SPACE}
    Check Test Case  ${TESTNAME}

\${EMPTY}
    Check Test Case  ${TESTNAME}

\@{EMPTY}
    Check Test Case  ${TESTNAME}

\&{EMPTY}
    Check Test Case  ${TESTNAME}

\@{EMPTY} and \&{EMPTY} cannot be modified
    Check Test Case  ${TESTNAME}

\${/}
    Check Test Case  ${TESTNAME}

\${:}
    Check Test Case  ${TESTNAME}

\${\\n}
    Check Test Case  ${TESTNAME}

\${TEMPDIR}
    Check Test Case  ${TESTNAME}

\${EXECDIR}
    Check Test Case  ${TESTNAME}

$CURDIR
    Check Test Case  ${TESTNAME}

\${LOG LEVEL}
    Check Test Case  ${TESTNAME}

Built-In Variables Cannot Be Overridden In Variable Table Or From CLI
    [Documentation]  Except for number variabels
    Check Test Case  ${TESTNAME}

Number Variables Can Be Overridden In Variable Table And From CLI
    Check Test Case  ${TESTNAME}

Built-In Variables Can Be Overridden In Local Scope
    [Documentation]  Actually $CURDIR cannot be ever overridden
    Check Test Case  ${TESTNAME} 1
    Check Test Case  ${TESTNAME} 2
