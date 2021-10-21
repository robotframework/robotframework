*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/inline_if_else.robot
Resource          atest_resource.robot

*** Test Cases ***
Inline if passing
    Check Test Case    ${TESTNAME}

Inline if failing
    Check Test Case    ${TESTNAME}

Inline if not executed
    Check Test Case    ${TESTNAME}

Inline if not executed failing
    Check Test Case    ${TESTNAME}

Inline if else - if executed
    Check Test Case    ${TESTNAME}

Inline if else - else executed
    Check Test Case    ${TESTNAME}

Inline if else - if executed - failing
    Check Test Case    ${TESTNAME}

Inline if else - else executed - failing
    Check Test Case    ${TESTNAME}

Assignment inside inline if
    Check Test Case    ${TESTNAME}

Inline if inside for loop
    Check Test Case    ${TESTNAME}

Inline if inside nested loop
    Check Test Case    ${TESTNAME}

Inline if passing in keyword
    Check Test Case    ${TESTNAME}

Inline if passing in else keyword
    Check Test Case    ${TESTNAME}

Inline if failing in keyword
    Check Test Case    ${TESTNAME}

Inline if failing in else keyword
    Check Test Case    ${TESTNAME}

Invalid END after inline header
    Check Test Case    ${TESTNAME}
