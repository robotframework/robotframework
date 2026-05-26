*** Settings ***
Documentation     Acceptance tests for the interactive step debugger
...               (`Debug` keyword in the Dialogs library). Driven
...               non-interactively via the FakeDebuggerDialog test
...               library, so these run on CI like normal atests.
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/dialogs/debug.robot
Resource          atest_resource.robot

*** Test Cases ***
Continue resumes immediately
    Check Test Case    ${TESTNAME}

Step In stops on the very next body item
    Check Test Case    ${TESTNAME}

Step Over skips nested user keyword body
    Check Test Case    ${TESTNAME}

Step Out runs to the caller
    Check Test Case    ${TESTNAME}

Multiple Debug calls each open the dialog
    Check Test Case    ${TESTNAME}

Abort ends the run
    Check Test Case    ${TESTNAME}
