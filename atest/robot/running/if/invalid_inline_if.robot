*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/invalid_inline_if.robot
Resource          atest_resource.robot

*** Test Cases ***
Invalid condition
    Check Test Case    ${TESTNAME}

Empty IF
    Check Test Case    ${TESTNAME}

IF without branch
    Check Test Case    ${TESTNAME}

IF without branch with ELSE IF
    Check Test Case    ${TESTNAME}

IF without branch with ELSE
    Check Test Case    ${TESTNAME}

IF follewed by ELSE IF
    Check Test Case    ${TESTNAME}

IF follewed by ELSE
    Check Test Case    ${TESTNAME}

Empty ELSE IF
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

ELSE IF without branch
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Empty ELSE
    Check Test Case    ${TESTNAME}

ELSE IF after ELSE
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Multiple ELSEs
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Nested IF
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3

Nested FOR
    Check Test Case    ${TESTNAME}

Unnecessary END
    Check Test Case    ${TESTNAME}

Assign in IF branch
    Check Test Case    ${TESTNAME}

Assign in ELSE IF branch
    Check Test Case    ${TESTNAME}

Assign in ELSE branch
    Check Test Case    ${TESTNAME}

Invalid assing mark usage
    Check Test Case    ${TESTNAME}

Too many list variables in assign
    Check Test Case    ${TESTNAME}

Invalid number of variables in assign
    Check Test Case    ${TESTNAME}

Invalid value for list assign
    Check Test Case    ${TESTNAME}

Invalid value for dict assign
    Check Test Case    ${TESTNAME}

Assign when IF branch is empty
    Check Test Case    ${TESTNAME}

Assign when ELSE IF branch is empty
    Check Test Case    ${TESTNAME}

Assign when ELSE branch is empty
    Check Test Case    ${TESTNAME}

Assign with RETURN
    Check Test Case    ${TESTNAME}
