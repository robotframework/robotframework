*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    standard_libraries/easter.robot
Resource        atest_resource.robot

*** Test Cases ***
Not None Shall Not Pass
    Check Test Case    ${TESTNAME}

None Shall Pass
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}
    ...    <iframe * src="https://www.youtube-nocookie.com/embed/*
    ...    HTML    pattern=yes
