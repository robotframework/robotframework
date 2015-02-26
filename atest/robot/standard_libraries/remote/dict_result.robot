*** Settings ***
Suite Setup      Run Remote Tests    dict_result.robot    dictresult.py
Force Tags       regression    pybot    jybot
Resource         remote_resource.robot

*** Test Cases ***
Dicts are returned correctly
    Check Test Case    ${TESTNAME}

Returned dicts are dot-accessible
    Check Test Case    ${TESTNAME}
