*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    running/prevent_recursion.robot
Resource         atest_resource.robot

*** Test Cases ***
Infinite recursion
    Check Test Case    ${TESTNAME}

Infinite cyclic recursion
    Check Test Case    ${TESTNAME}

Infinite recursion with Run Keyword
    Check Test Case    ${TESTNAME}

Infinitely recursive for loop
    Check Test Case    ${TESTNAME}

Recursion below the recursion limit is ok
    [Documentation]    Also verifies that recursion limit blown earlier doesn't affect subsequent tests
    Check Test Case    ${TESTNAME}

