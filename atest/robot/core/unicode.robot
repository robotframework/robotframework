*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  misc/unicode.robot core/unicode_failure_in_suite_setup_and_teardown.robot
Resource        atest_resource.robot
Variables       unicode_vars.py

*** Test Cases ***
Unicode In Log Messages
    ${tc} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  ${MESSAGE1}
    Check Log Message  ${tc.kws[0].msgs[1]}  ${MESSAGE2}
    Check Log Message  ${tc.kws[0].msgs[2]}  ${MESSAGE3}

Unicode Return Value
    ${tc} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[2].msgs[0]}  Français

Unicode In Return Value Attributes
    ${tc} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  ${MESSAGES}
    Check Log Message  ${tc.kws[0].msgs[1]}  \${obj} = ${MESSAGES}
    Check Log Message  ${tc.kws[1].msgs[0]}  ${MESSAGES}

Unicode Failure
    ${tc} =  Check Test Case  ${TESTNAME}  FAIL  ${MESSAGES}
    Check Log Message  ${tc.kws[0].msgs[0]}  ${MESSAGES}  FAIL

Unicode Failure In Setup
    ${tc} =  Check Test Case  ${TESTNAME}  FAIL  Setup failed:\n ${MESSAGES}
    Check Log Message  ${tc.setup.msgs[0]}  ${MESSAGES}  FAIL

Unicode Failure In Teardown
    ${tc} =  Check Test Case  ${TESTNAME}  FAIL  Teardown failed:\n ${MESSAGES}
    Check Log Message  ${tc.teardown.msgs[0]}  ${MESSAGES}  FAIL

Unicode Failure In Teardown After Normal Failure
    Check Test Case  ${TESTNAME}  FAIL  Just ASCII here\n\n Also teardown failed:\n ${MESSAGES}

Unicode Failure In Suite Setup and Teardown
    Check Test Case  ${TESTNAME}
    Check Log Message  ${SUITE.suites[1].setup.msgs[0]}  ${MESSAGES}  FAIL
    Check Log Message  ${SUITE.suites[1].teardown.msgs[0]}  ${MESSAGES}  FAIL

Ünïcödë Tëst änd Këywörd Nämës
    ${tc} =  Check Test Case  ${TESTNAME}
    Should Be Equal  ${tc.kws[0].name}  Ünïcödë Këywörd Nämë
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  Hyvää päivää
