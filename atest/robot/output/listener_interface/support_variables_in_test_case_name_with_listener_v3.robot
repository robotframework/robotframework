*** Settings ***
Suite Setup      Run Tests    --listener ${DATADIR}/output/listeners/verify_var_name_in_test_case_v3.py    output/listeners/support_variables_in_test_case_name.robot
Resource         atest_resource.robot

*** Test Cases ***
Test Case Name With Variable
    Check Test Case    ${TESTNAME}    PASS    
    ...    [Start] [data] Test Case \${NAME} With \${VARIABLE} [result] Test Case Name With Variable [END] [data] Test Case \${NAME} With \${VARIABLE} [result] Test Case Name With Variable

Test Case Name With ['My', 'List']
    Check Test Case    ${TESTNAME}    PASS
    ...    [Start] [data] Test Case \${NAME} With \${MY LIST} [result] Test Case Name With ['My', 'List'] [END] [data] Test Case \${NAME} With \${MY LIST} [result] Test Case Name With ['My', 'List']

Test Case Name With {'key': 'value'}
    Check Test Case    ${TESTNAME}    PASS
    ...    [Start] [data] Test Case \${NAME} With \${MY DICT} [result] Test Case Name With {'key': 'value'} [END] [data] Test Case \${NAME} With \${MY DICT} [result] Test Case Name With {'key': 'value'}

Test Case Name With \${UNKONW VARIABLE}
    Check Test Case    ${TESTNAME}    PASS
    ...    [Start] [data] Test Case \${NAME} With \${UNKONW VARIABLE} [result] Test Case Name With \${UNKONW VARIABLE} [END] [data] Test Case \${NAME} With \${UNKONW VARIABLE} [result] Test Case Name With \${UNKONW VARIABLE}
