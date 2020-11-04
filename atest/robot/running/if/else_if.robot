*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/else_if.robot
Resource          atest_resource.robot

*** Test Cases ***
Else if condition 1 passes
  Check Test Case    ${TESTNAME}

Else if condition 2 passes
  Check Test Case    ${TESTNAME}

Else if else passes
  Check Test Case    ${TESTNAME}

Else if condition 1 failing
  Check Test Case    ${TESTNAME}

Else if condition 2 failing
  Check Test Case    ${TESTNAME}

Else if else failing
  Check Test Case    ${TESTNAME}