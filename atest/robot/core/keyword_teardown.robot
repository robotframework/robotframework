*** Settings ***
Resource     atest_resource.robot
Suite Setup  Run Tests  ${EMPTY}  core/keyword_teardown.robot

*** Test Cases ***
Passing Keyword with Teardown
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  In UK
    Check Log Message  ${tc.kws[0].teardown.msgs[0]}  In UK Teardown

Failing Keyword with Teardown
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  Expected Failure!  FAIL
    Check Log Message  ${tc.kws[0].teardown.msgs[0]}  In Failing UK Teardown

Teardown in keyword with embedded arguments
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  In UK with Embedded Arguments
    Check Log Message  ${tc.kws[0].teardown.msgs[0]}  In Teardown of UK with Embedded Arguments
    Check Log Message  ${tc.kws[1].kws[0].msgs[0]}  Expected Failure in UK with Embedded Arguments  FAIL
    Check Log Message  ${tc.kws[1].teardown.msgs[0]}  In Teardown of Failing UK with Embedded Arguments

Failure in Keyword Teardown
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  In UK
    Check Log Message  ${tc.kws[0].teardown.msgs[0]}  Failing in UK Teardown  FAIL

Failures in Keyword and Teardown
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  Expected Failure!  FAIL
    Check Log Message  ${tc.kws[0].teardown.msgs[0]}  Failing in UK Teardown  FAIL

Multiple Failures in Keyword Teardown
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].teardown.kws[0].msgs[0]}  Failure in Teardown  FAIL
    Check Log Message  ${tc.kws[0].teardown.kws[1].kws[0].msgs[0]}  Expected Failure!  FAIL
    Check Log Message  ${tc.kws[0].teardown.kws[1].kws[1].msgs[0]}  Executed if in nested Teardown
    Check Log Message  ${tc.kws[0].teardown.kws[2].msgs[0]}  Third failure in Teardown  FAIL

Nested Keyword Teardowns
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].kws[0].kws[0].msgs[0]}  In UK
    Check Log Message  ${tc.kws[0].kws[0].teardown.msgs[0]}  In UK Teardown
    Check Log Message  ${tc.kws[0].teardown.kws[0].msgs[0]}  In UK
    Check Log Message  ${tc.kws[0].teardown.teardown.msgs[0]}  In UK Teardown

Nested Keyword Teardown Failures
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].kws[0].teardown.msgs[0]}  Failing in UK Teardown  FAIL
    Check Log Message  ${tc.kws[0].teardown.msgs[0]}  Failing in outer UK Teardown  FAIL

Continuable Failure in Keyword
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].kws[0].kws[0].msgs[0]}  Please continue  FAIL
    Check Log Message  ${tc.kws[0].kws[1].msgs[0]}  After continuable failure
    Check Log Message  ${tc.kws[0].teardown.msgs[0]}  In UK Teardown

Non-ASCII Failure in Keyword Teardown
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  åäö
    Check Log Message  ${tc.kws[0].teardown.msgs[0]}  Hyvää äitienpäivää!  FAIL

Keyword cannot have only teardown
    Check Test Case  ${TESTNAME}

Replacing Variables in Keyword Teardown Fails
    Check Test Case  ${TESTNAME}
