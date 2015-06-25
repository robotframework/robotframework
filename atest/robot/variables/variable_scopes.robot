*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/variable_scopes.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Variables Set In One Test Are Not Visible In Another
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Variables do not leak
    Check Test Case    ${TESTNAME}

Variables can be passed as arguments
    Check Test Case    ${TESTNAME}

Set test variable
    Check Test Case    ${TESTNAME}
