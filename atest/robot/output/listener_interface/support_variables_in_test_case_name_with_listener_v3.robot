*** Settings ***
Suite Setup      Run Tests    --listener ${DATADIR}/output/listeners/verify_var_name_in_test_case_v3.py    output/listeners/support_variables_in_test_case_name.robot
Resource         atest_resource.robot

*** Test Cases ***
Test Case Name With Variable
    Check Test Case    Test Case \${NAME} With \${VARIABLE}    PASS
    ...    [Start] [data] Test Case \${NAME} With \${VARIABLE} [result] ${TESTNAME} [END] [data] Test Case \${NAME} With \${VARIABLE} [result] ${TESTNAME}

Test Case Name With ['My', 'List']
    Check Test Case    Test Case \${NAME} With \${MY LIST}    PASS
    ...    [Start] [data] Test Case \${NAME} With \${MY LIST} [result] ${TESTNAME} [END] [data] Test Case \${NAME} With \${MY LIST} [result] ${TESTNAME}

Test Case Name With {'key': 'value'}
    Check Test Case    Test Case \${NAME} With \${MY DICT}    PASS
    ...    [Start] [data] Test Case \${NAME} With \${MY DICT} [result] ${TESTNAME} [END] [data] Test Case \${NAME} With \${MY DICT} [result] ${TESTNAME}

Test Case Name With \${UNKONW VARIABLE}
    Check Test Case    Test Case \${NAME} With \${UNKONW VARIABLE}    PASS
    ...    [Start] [data] Test Case \${NAME} With \${UNKONW VARIABLE} [result] ${TESTNAME} [END] [data] Test Case \${NAME} With \${UNKONW VARIABLE} [result] ${TESTNAME}
