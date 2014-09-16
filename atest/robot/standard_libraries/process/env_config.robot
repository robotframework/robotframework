*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/env_config.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
By default environ is got from system
    Check Test Case    ${TESTNAME}

Giving whole environ
    Check Test Case    ${TESTNAME}

Giving individual values
    Check Test Case    ${TESTNAME}

Giving multiple values separately
    Check Test Case    ${TESTNAME}

Invividually given overrides system variable
    Check Test Case    ${TESTNAME}

Invividually given overrides value in given environ
    Check Test Case    ${TESTNAME}
