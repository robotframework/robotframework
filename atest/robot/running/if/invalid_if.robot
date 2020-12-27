*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/invalid_if.robot
Resource          atest_resource.robot

*** Test Cases ***
If without condition
  Check Test Case    ${TESTNAME}

If with many conditions
  Check Test Case    ${TESTNAME}

If without end
  Check Test Case    ${TESTNAME}

Invalid END
  Check Test Case    ${TESTNAME}

If with wrong case
  Check Test Case    ${TESTNAME}

Else if without condition
  Check Test Case    ${TESTNAME}

Else if with multiple conditions
  Check Test Case    ${TESTNAME}

Else with a condition
  Check Test Case    ${TESTNAME}

If with empty if
  Check Test Case    ${TESTNAME}

If with empty else
  Check Test Case    ${TESTNAME}

If with empty else_if
  Check Test Case    ${TESTNAME}

If with else after else
  Check Test Case    ${TESTNAME}

If with else if after else
  Check Test Case    ${TESTNAME}

If for else if parsing
  Check Test Case    ${TESTNAME}

Multiple errors
  Check Test Case    ${TESTNAME}
