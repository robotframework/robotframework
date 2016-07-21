*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/run_keyword_and_return_status.robot
Resource        atest_resource.robot


*** Test Cases ***

Should return True when keyword Succeeds
    Check Test Case  ${TESTNAME}

Should return False when keyword Fails
    Check Test Case  ${TESTNAME}
