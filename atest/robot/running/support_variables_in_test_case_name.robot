*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    running/support_variables_in_test_case_name.robot
Resource         atest_resource.robot

*** Test Cases ***
Test Case Name With Variable
    Check Test Case    ${TESTNAME}

Test Case Name With ['My', 'List']
    Check Test Case    ${TESTNAME}

Test Case Name With {'key': 'value'}
    Check Test Case    ${TESTNAME}

Test Case Name With \${UNKONW VARIABLE}
    Check Test Case    ${TESTNAME}
