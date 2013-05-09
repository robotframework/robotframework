*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/scalar_as_list.txt
Force Tags       regression    pybot    jybot
Resource         atest_resource.txt

*** Test Cases ***
Scalar List As List Variable
    Check Test Case    ${TESTNAME}

Scalar Iterable As List Variable
    Check Test Case    ${TESTNAME}

Scalar Variable As List With Extended Syntax
    Check Test Case    ${TESTNAME}

Non-alphanumeric characters in name
    Check Test Case    ${TESTNAME}

String Cannot Be Used As List Variable
    Check Test Case    ${TESTNAME}

Non-Iterables Cannot Be Used As List Variable
    Check Test Case    ${TESTNAME}
