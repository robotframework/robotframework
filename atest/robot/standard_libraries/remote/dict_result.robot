*** Settings ***
Suite Setup      Run Remote Tests    dict_result.robot    dictresult.py
Resource         remote_resource.robot

*** Test Cases ***
Dicts are returned correctly
    Check Test Case    ${TESTNAME}

Returned dicts are dot-accessible
    Check Test Case    ${TESTNAME}
