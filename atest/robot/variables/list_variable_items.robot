*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/list_variable_items.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Valid index
    Check Test Case    ${TESTNAME}

Valid index using variable
    Check Test Case    ${TESTNAME}

Invalid index
    Check Test Case    ${TESTNAME}

Invalid index using variable
    Check Test Case    ${TESTNAME}

Non-string index
    Check Test Case    ${TESTNAME}

Non-string index using variable
    Check Test Case    ${TESTNAME}

Non-existing list variable
    Check Test Case    ${TESTNAME}

Non-existing index variable
    Check Test Case    ${TESTNAME}
