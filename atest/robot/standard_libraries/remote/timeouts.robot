*** Settings ***
Suite Setup      Run Remote Tests    timeouts.robot    timeouts.py
Resource         remote_resource.robot

*** Test Cases ***
Initial connection failure
    Check Test Case    ${TESTNAME}

Too long keyword execution time
    Check Test Case    ${TESTNAME}
