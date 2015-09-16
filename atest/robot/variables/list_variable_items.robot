*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/list_variable_items.robot
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

Non-int index
    Check Test Case    ${TESTNAME}

Non-int index using variable
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Empty index
    Check Test Case    ${TESTNAME}

Non-existing list variable
    Check Test Case    ${TESTNAME}

Non-existing index variable
    Check Test Case    ${TESTNAME}
