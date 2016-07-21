*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/easter.robot
Resource        atest_resource.robot


*** Test Cases ***

Not None Shall Not Pass
    Check Test Case  ${TESTNAME}

None Shall Pass
    ${tc} =  Check Test Case  ${TESTNAME}
    Should Contain  ${tc.kws[0].msgs[0].message}  youtube.com
    Should Be Equal  ${tc.kws[0].msgs[0].level}  INFO
