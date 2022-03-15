*** Settings ***
Suite Setup       Run Tests    -v space:space -v -1:negative    variables/builtin_variables_can_be_overridden.robot
Resource          atest_resource.robot

*** Test Cases ***
Overridden from CLI
    Check Test Case    ${TESTNAME}

Overridden in variables section
    Check Test Case    ${TESTNAME}

Overridden in resource file
    Check Test Case    ${TESTNAME}

Overridden locally
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
